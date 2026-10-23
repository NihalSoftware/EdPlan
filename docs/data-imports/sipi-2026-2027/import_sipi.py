"""Import the reviewed SIPI academic catalog into the user-confirmed Render database.
Dry-run by default. Only academic tables are accessed; credentials are never printed.
"""
import argparse,collections,hashlib,json,pathlib,sys,uuid
from decimal import Decimal
from urllib.parse import urlsplit
from dotenv import dotenv_values
import psycopg2
from psycopg2.extras import Json,RealDictCursor,execute_values
from extract_sipi import build,validate
HERE=pathlib.Path(__file__).resolve().parent

def fingerprint(cur,university_id):
    queries={
      'universities':"SELECT u.university_id AS id,to_jsonb(u)::text AS row FROM public.universities u WHERE u.university_id<>%s",
      'programs':"SELECT p.program_id AS id,to_jsonb(p)::text AS row FROM public.programs p WHERE p.university_id<>%s",
      'courses':"SELECT c.course_id AS id,to_jsonb(c)::text AS row FROM public.courses c JOIN public.programs p USING(program_id) WHERE p.university_id<>%s"
    }
    result={}
    for table,query in queries.items():
        cur.execute("SELECT count(*),md5(COALESCE(string_agg(md5(row),'' ORDER BY id),'')) FROM ("+query+") snapshot",(university_id,))
        result[table]=list(cur.fetchone())
    return result

def program_metadata(data,program,source_id):
    return {**program['metadata_json'],'degree':program['degree'],'program':program['program_name'],
      'catalog_year':data['source']['catalog_year'],'catalog_source':data['source']['filename'],
      'catalog_title':data['source']['catalog_title'],'source_sha256':data['source']['sha256'],
      'source_pdf_pages':program['source_pdf_pages'],'source_printed_pages':program['source_printed_pages'],
      'source_requirements_text':program['source_requirements_text'],'total_credit_hours':program['total_credit_hours'],
      'is_current_catalog':data['source']['is_current_catalog'],'catalog_import_id':source_id}

def connect_database(env_file):
    url=dotenv_values(env_file).get('DATABASE_URL')
    if not url or not (urlsplit(url).hostname or '').startswith('dpg-d4rap9qdbo4c73c8rr3g-a'):
        raise RuntimeError('Configured database differs from confirmed Render instance')
    conn=psycopg2.connect(url.replace('postgresql+asyncpg://','postgresql://',1),connect_timeout=10)
    if not conn.info.ssl_in_use:
        conn.close();raise RuntimeError('TLS required')
    return conn

def profile_metadata(data):
    return {'catalog_year':data['source']['catalog_year'],'source_filename':data['source']['filename'],
       'catalog_institution_name':data['institution']['catalog_institution_name'],'abbreviation':'SIPI',
       'source_sha256':data['source']['sha256'],'is_current_catalog':True,
       'source_pdf_page_count':57,'source_printed_page_range':[61,117],
       'program_count':len(data['programs']),'course_row_count':len(data['courses']),
       'held_programs':data['held_programs'],'needs_clarification':data['needs_clarification'],
       'held_course_row_count':len(data['held_course_rows']),
       'unresolved_requirement_slot_count':len(data['unresolved_requirement_slots']),
       'catalog_import_status':'partial','course_import_is_partial':True,'planning_ready':False}

def course_metadata(data,course,source_id):
    return {**course['metadata_json'],'catalog_import_id':source_id,
        'source_sha256':data['source']['sha256'],'catalog_year':data['source']['catalog_year'],
        'source_filename':data['source']['filename'],'course_import_is_partial':True}

def run():
    parser=argparse.ArgumentParser()
    parser.add_argument('--apply',action='store_true')
    parser.add_argument('--env-file',default='D:/EdPlan/fastapi_backend/.env')
    parser.add_argument('--source-pdf',default='C:/Users/hp/Downloads/SOUTHWESTERN INDIAN POLYTECHNIC INSTITUTE.pdf')
    args=parser.parse_args();conn=None
    try:
        data=json.loads((HERE/'sipi-import-data.json').read_text(encoding='utf-8'))
        validate(data)
        if build()!=data:raise RuntimeError('Dataset differs from reproducible extraction')
        if hashlib.sha256(pathlib.Path(args.source_pdf).read_bytes()).hexdigest()!=data['source']['sha256']:
            raise RuntimeError('Source PDF fingerprint differs')
        source_id='sipi-2627-'+data['source']['sha256'][:12]
        conn=connect_database(args.env_file);conn.set_session(isolation_level='SERIALIZABLE')
        cur=conn.cursor()
        cur.execute("SET LOCAL lock_timeout = '10s'")
        cur.execute("SET LOCAL statement_timeout = '60s'")
        cur.execute("SELECT current_database()")
        if cur.fetchone()[0]!='edplan_db':raise RuntimeError('Unexpected database identity')
        cur.execute("SELECT pg_advisory_xact_lock(hashtext('SIPI-catalog-import'))")
        college=data['institution']
        cur.execute("SELECT university_id FROM public.universities WHERE university_name=%s AND city=%s AND state=%s FOR UPDATE",
          (college['university_name'],college['city'],college['state']))
        rows=cur.fetchall()
        if len(rows)!=1:raise RuntimeError('Expected exactly one existing SIPI college record')
        university_id=str(rows[0][0]);before=fingerprint(cur,university_id)
        with conn.cursor(cursor_factory=RealDictCursor) as bcur:
            bcur.execute("SELECT * FROM public.universities WHERE university_id=%s",(university_id,))
            backup={'universities':bcur.fetchall()}
            bcur.execute("SELECT * FROM public.programs WHERE university_id=%s",(university_id,))
            backup['programs']=bcur.fetchall()
            bcur.execute("SELECT c.* FROM public.courses c JOIN public.programs p USING(program_id) WHERE p.university_id=%s",(university_id,))
            backup['courses']=bcur.fetchall()
        backup_path=HERE/'sipi-before-import.json'
        if not backup_path.exists():backup_path.write_text(json.dumps(backup,default=str,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        baseline=json.loads(backup_path.read_text(encoding='utf-8'))
        if str(baseline['universities'][0]['university_id'])!=university_id:raise RuntimeError('Backup identity mismatch')
        if baseline['programs'] or baseline['courses']:raise RuntimeError('Baseline differs from the reviewed empty SIPI academic catalog')
        inserted_programs=[];program_ids={}
        for program in data['programs']:
            key=program['program_name']+' | '+program['degree'];meta=program_metadata(data,program,source_id)
            official_id=source_id+':'+uuid.uuid5(uuid.NAMESPACE_URL,key).hex[:12]
            cur.execute("INSERT INTO public.programs (university_id,program_name,degree,total_credit_hours,metadata_json,official_source_id,source_retrieved_at) VALUES (%s,%s,%s,%s,%s,%s,now()) ON CONFLICT (university_id,program_name,degree) DO NOTHING RETURNING program_id",
              (university_id,program['program_name'],program['degree'],program['total_credit_hours'],Json(meta),official_id))
            row=cur.fetchone()
            if row:pid=str(row[0]);inserted_programs.append(pid)
            else:
                cur.execute("SELECT program_id,total_credit_hours,metadata_json,official_source_id FROM public.programs WHERE university_id=%s AND program_name=%s AND degree=%s",
                  (university_id,program['program_name'],program['degree']))
                existing=cur.fetchone()
                if existing[1]!=program['total_credit_hours'] or existing[2]!=meta or existing[3]!=official_id:
                    raise RuntimeError('Existing program conflicts; refusing to overwrite')
                pid=str(existing[0])
            program_ids[key]=pid
        cur.execute("SELECT program_id,course_id,course_code,credits,course_name,metadata_json,recommended_year,recommended_semester,lecture_hours,lab_hours FROM public.courses WHERE program_id=ANY(%s::uuid[])",
          (list(program_ids.values()),))
        existing=collections.defaultdict(list)
        for row in cur.fetchall():existing[(str(row[0]),row[2])].append(row)
        pending=[];inserted_courses=[]
        for course in data['courses']:
            pid=program_ids[course['program_key']];meta=course_metadata(data,course,source_id)
            matches=existing[(pid,course['course_code'])]
            if matches:
                if len(matches)!=1:raise RuntimeError('Duplicate existing course identifiers')
                row=matches[0]
                if row[3]!=Decimal(str(course['credits'])) or row[4]!=course['course_name'] or row[5]!=meta or any(v is not None for v in row[6:]):
                    raise RuntimeError('Existing course conflicts; refusing to overwrite')
                continue
            cid=str(uuid.uuid4());inserted_courses.append(cid)
            official_id=source_id+':'+uuid.uuid5(uuid.NAMESPACE_URL,course['program_key']+':'+course['course_code']).hex[:12]
            pending.append((cid,pid,course['course_code'],course['course_name'],course['credits'],Json(meta),course['source_sequence'],official_id))
        if pending:
            execute_values(cur,"INSERT INTO public.courses (course_id,program_id,course_code,course_name,credits,metadata_json,source_sequence,official_source_id,source_retrieved_at) VALUES %s",
                pending,template="(%s,%s,%s,%s,%s,%s,%s,%s,now())",page_size=500)
        profile=profile_metadata(data)
        cur.execute("SELECT college_profile FROM public.universities WHERE university_id=%s",(university_id,))
        current=cur.fetchone()[0] or {}
        if current.get('sipi_catalog_import') not in (None,profile):raise RuntimeError('Existing SIPI profile conflicts')
        preserved={k:v for k,v in current.items() if k!='sipi_catalog_import'}
        if preserved!=(baseline['universities'][0]['college_profile'] or {}):raise RuntimeError('Original college profile differs')
        if current.get('sipi_catalog_import')!=profile:
            cur.execute("UPDATE public.universities SET college_profile=COALESCE(college_profile,'{}'::jsonb)||jsonb_build_object('sipi_catalog_import',%s::jsonb) WHERE university_id=%s",(Json(profile),university_id))
        cur.execute("SELECT count(*) FROM public.programs WHERE university_id=%s",(university_id,))
        assert cur.fetchone()[0]==len(data['programs'])
        cur.execute("SELECT count(*) FROM public.courses c JOIN public.programs p USING(program_id) WHERE p.university_id=%s",(university_id,))
        assert cur.fetchone()[0]==len(data['courses'])
        assert fingerprint(cur,university_id)==before,'Other college academic data changed'
        result={'mode':'applied' if args.apply else 'dry-run-rolled-back','database':'edplan_db',
          'university_id':university_id,'program_count':len(data['programs']),'course_row_count':len(data['courses']),
          'held_program_count':len(data['held_programs']),'inserted_program_ids':inserted_programs,
          'inserted_course_ids':inserted_courses,'program_ids':program_ids,'other_colleges_unchanged':True,
          'other_college_fingerprints':before,'original_college_profile_preserved':True,'source_sha256':data['source']['sha256']}
        if args.apply:conn.commit()
        else:conn.rollback()
        (HERE/('applied.json' if args.apply else 'dry-run.json')).write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({k:v for k,v in result.items() if not k.endswith('_ids') and k!='other_college_fingerprints'},indent=2))
        print('New program rows:',len(inserted_programs),'New course rows:',len(inserted_courses))
    except Exception as error:
        if conn:conn.rollback()
        print('Import rolled back:',type(error).__name__,getattr(error,'pgcode',None))
        raise SystemExit(1) from None
    finally:
        if conn:conn.close()
if __name__=='__main__':run()
