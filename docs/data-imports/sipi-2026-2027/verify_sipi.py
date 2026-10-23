"""Read-only comparison of the saved SIPI catalog with the reviewed source dataset."""
import collections,json,pathlib,sys
from decimal import Decimal
from import_sipi import connect_database,fingerprint,program_metadata,course_metadata,profile_metadata
HERE=pathlib.Path(__file__).resolve().parent
def run():
    conn=None
    try:
        data=json.loads((HERE/'sipi-import-data.json').read_text(encoding='utf-8'))
        applied=json.loads((HERE/'applied.json').read_text(encoding='utf-8'))
        baseline=json.loads((HERE/'sipi-before-import.json').read_text(encoding='utf-8'))
        sid='sipi-2627-'+data['source']['sha256'][:12];uid=applied['university_id']
        conn=connect_database('D:/EdPlan/fastapi_backend/.env');conn.set_session(readonly=True,isolation_level='REPEATABLE READ')
        cur=conn.cursor();cur.execute("SELECT current_database()");assert cur.fetchone()[0]=='edplan_db'
        cur.execute("SELECT to_jsonb(u) FROM public.universities u WHERE university_id=%s",(uid,))
        college=cur.fetchone()[0];original=baseline['universities'][0]
        for key,value in original.items():
            if key!='college_profile':assert college[key]==value,key
        profile=college['college_profile'];assert profile.pop('sipi_catalog_import')==profile_metadata(data)
        assert profile==(original['college_profile'] or {})
        cur.execute("SELECT program_id,program_name,degree,total_credit_hours,metadata_json,official_source_id,official_source_url,source_retrieved_at FROM public.programs WHERE university_id=%s",(uid,))
        program_rows=cur.fetchall();assert len(program_rows)==len(data['programs'])==15
        index={(r[1],r[2]):r for r in program_rows};by_id={}
        for spec in data['programs']:
            r=index[(spec['program_name'],spec['degree'])]
            assert r[3]==spec['total_credit_hours'] and r[4]==program_metadata(data,spec,sid)
            assert r[5].startswith(sid+':') and r[6] is None and r[7] is not None
            by_id[str(r[0])]=spec['program_name']+' | '+spec['degree']
        cur.execute("SELECT c.program_id,c.course_code,c.course_name,c.credits,c.lecture_hours,c.lab_hours,c.recommended_year,c.recommended_semester,c.metadata_json,c.source_sequence,c.official_source_id,c.official_source_url,c.source_retrieved_at,c.semester_number,c.recommended_term_number FROM public.courses c JOIN public.programs p USING(program_id) WHERE p.university_id=%s",(uid,))
        rows=cur.fetchall();assert len(rows)==len(data['courses'])==187
        expected={(c['program_key'],c['course_code']):c for c in data['courses']}
        seen=set();counts=collections.Counter()
        for r in rows:
            key=(by_id[str(r[0])],r[1]);assert key not in seen;seen.add(key)
            spec=expected[key];counts[key[0]]+=1
            assert r[2]==spec['course_name'] and r[3]==Decimal(str(spec['credits']))
            assert all(x is None for x in r[4:8])
            assert r[8]==course_metadata(data,spec,sid) and r[9]==spec['source_sequence']
            assert r[10].startswith(sid+':') and r[11] is None and r[12] is not None
            assert r[13] is None and r[14] is None
        assert seen==set(expected)
        assert fingerprint(cur,uid)==applied['other_college_fingerprints']
        cur.execute("SELECT u.university_name,count(DISTINCT p.program_id),count(c.course_id) FROM public.universities u LEFT JOIN public.programs p USING(university_id) LEFT JOIN public.courses c USING(program_id) WHERE u.university_name IN ('Institute of American Indian Arts','Mesalands Community College','New Mexico Military Institute') GROUP BY u.university_name")
        prior=[list(r) for r in cur.fetchall()]
        result={'database':'edplan_db','verified_program_count':len(program_rows),'verified_course_row_count':len(rows),
            'exact_program_and_course_metadata_match':True,'original_college_record_preserved':True,
            'other_colleges_unchanged':True,'unknown_hours_and_schedules_remain_null':True,
            'previous_import_counts':prior,'per_program_course_counts':counts,'source_sha256':data['source']['sha256']}
        conn.rollback()
        (HERE/'verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(result,indent=2))
    except Exception as error:
        if conn:conn.rollback()
        print('Verification failed:',type(error).__name__,getattr(error,'pgcode',None));raise SystemExit(1) from None
    finally:
        if conn:conn.close()
if __name__=='__main__':run()
