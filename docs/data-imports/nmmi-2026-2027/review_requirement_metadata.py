"""Remove inferred category caps from this import only; preserve the explicit leadership range."""
import json,pathlib,sys
from psycopg2.extras import Json
from import_nmmi import connect_database,fingerprint
HERE=pathlib.Path(__file__).resolve().parent
conn=None
try:
    applied=json.loads((HERE/'applied.json').read_text(encoding='utf-8'))
    uid=applied['university_id'];conn=connect_database('D:/EdPlan/fastapi_backend/.env')
    conn.set_session(isolation_level='SERIALIZABLE');cur=conn.cursor()
    cur.execute("SELECT current_database()");assert cur.fetchone()[0]=='edplan_db'
    cur.execute("SELECT pg_advisory_xact_lock(hashtext('NMMI-catalog-import'))")
    before=fingerprint(cur,uid)
    cur.execute("SELECT program_id,metadata_json FROM public.programs WHERE university_id=%s FOR UPDATE",(uid,))
    rows=cur.fetchall();assert len(rows)==2
    changed=0
    for pid,meta in rows:
        assert meta['source_sha256']==applied['source_sha256']
        assert str(pid) in applied['program_ids']
        old=json.loads(json.dumps(meta))
        for req in meta['core_credit_requirements']:
            if req['category']!='Military Science/Leadership':
                req.pop('maximum_credit_hours',None)
        if meta!=old:
            cur.execute("UPDATE public.programs SET metadata_json=%s WHERE program_id=%s AND metadata_json=%s",(Json(meta),pid,Json(old)))
            assert cur.rowcount==1;changed+=1
    assert fingerprint(cur,uid)==before
    conn.commit()
    result={'updated_imported_program_metadata_rows':changed,'reason':'Category totals are requirements, not explicit maximum caps; only the stated 2-12 leadership range retains a maximum.','other_colleges_unchanged':True}
    (HERE/'requirement-metadata-review.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result))
except Exception as error:
    if conn:conn.rollback()
    print('Metadata correction rolled back:',type(error).__name__,getattr(error,'pgcode',None));raise SystemExit(1) from None
finally:
    if conn:conn.close()
