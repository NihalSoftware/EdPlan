"""Read-only verification of the NMMI import; academic catalog tables only."""
import json,pathlib,sys
from import_nmmi import connect_database,fingerprint,program_metadata,profile_metadata
HERE=pathlib.Path(__file__).resolve().parent
def run():
    conn=None
    try:
        data=json.loads((HERE/'nmmi-import-data.json').read_text(encoding='utf-8'))
        applied=json.loads((HERE/'applied.json').read_text(encoding='utf-8'))
        baseline=json.loads((HERE/'nmmi-before-import.json').read_text(encoding='utf-8'))
        source_id='nmmi-2627-'+data['source']['sha256'][:12]
        conn=connect_database('D:/EdPlan/fastapi_backend/.env')
        conn.set_session(readonly=True,isolation_level='REPEATABLE READ')
        cur=conn.cursor()
        cur.execute("SELECT current_database()")
        assert cur.fetchone()[0]=='edplan_db'
        uid=applied['university_id']
        cur.execute("SELECT to_jsonb(u) FROM public.universities u WHERE university_id=%s",(uid,))
        college=cur.fetchone()[0]
        previous=baseline['universities'][0]
        for key,value in previous.items():
            if key!='college_profile':assert college[key]==value,key
        profile=college['college_profile']
        assert profile.pop('nmmi_catalog_import')==profile_metadata(data)
        assert profile==previous['college_profile']
        cur.execute("SELECT program_name,degree,total_credit_hours,metadata_json,official_source_id,official_source_url,source_retrieved_at FROM public.programs WHERE university_id=%s",(uid,))
        rows=cur.fetchall()
        assert len(rows)==2
        indexed={(r[0],r[1]):r for r in rows}
        concentrations=0
        for spec in data['programs']:
            r=indexed[(spec['program_name'],spec['degree'])]
            assert r[2]==spec['total_credit_hours']==60
            assert r[3]==program_metadata(data,spec,source_id)
            assert r[4].startswith(source_id+':') and r[5] is None and r[6] is not None
            assert not r[3]['planning_ready'] and r[3]['course_rows_imported']==0
            concentrations+=len(r[3]['concentrations'])
        assert concentrations==19
        cur.execute("SELECT count(*) FROM public.courses c JOIN public.programs p USING(program_id) WHERE p.university_id=%s",(uid,))
        assert cur.fetchone()[0]==0
        after=fingerprint(cur,uid)
        assert after==applied['other_college_fingerprints']
        # Confirm the earlier catalog imports still exist; no user tables queried.
        cur.execute("SELECT u.university_name,count(DISTINCT p.program_id),count(c.course_id) FROM public.universities u LEFT JOIN public.programs p USING(university_id) LEFT JOIN public.courses c USING(program_id) WHERE u.university_name IN ('Institute of American Indian Arts','Mesalands Community College') GROUP BY u.university_name")
        prior=[list(r) for r in cur.fetchall()]
        result={'database':'edplan_db','verified_program_count':len(rows),'verified_concentration_count':concentrations,
                'course_rows':0,'exact_program_metadata_match':True,'college_record_preserved':True,
                'other_colleges_unchanged':True,'previous_import_counts':prior,'source_sha256':data['source']['sha256']}
        conn.rollback()
        (HERE/'verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(result,indent=2))
    except Exception as error:
        if conn:conn.rollback()
        print('Verification failed:',type(error).__name__,getattr(error,'pgcode',None))
        raise SystemExit(1) from None
    finally:
        if conn:conn.close()
if __name__=='__main__':run()
