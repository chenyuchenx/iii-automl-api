from fastapi import APIRouter, Request, HTTPException, status, Query
from fastapi.responses import JSONResponse
from config import configs as p
import app.database as db, requests, json, app.src as src, app.logs as log

router = APIRouter()
services = APIRouter()
MongoDB   = db.MongoDB()

@router.post("/login", status_code=status.HTTP_200_OK)
def login(*, username: str = Query(...), password: str = Query(...), request: Request):

    query = {
        "query": "mutation signIn($input: SignInInput!) { signIn(input: $input) {user { id name username } ifpToken } }",
        "variables": {"input": {"username": username, "password": password}},
        }
    try:
        r = requests.request("POST", p.IFP_DESK_API_URL, json=query, timeout=4, verify=p.SKIP_TLS)
        res = json.loads(r.text)
        if res.get('errors') is not None:
            raise HTTPException(status_code=401, detail=f"{res.get('errors')}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")
    
    IFPToken   = r.cookies.get_dict().get("IFPToken")
    EIToken    = r.cookies.get_dict().get("EIToken")

    response = JSONResponse(content=res)
    response.set_cookie(key="IFPToken", value=IFPToken)
    response.set_cookie(key="EIToken", value=EIToken)

    return response

@router.get("/tokenvalidation", status_code=status.HTTP_200_OK)
async def tokenvalidation(request: Request):

    Cookie = {True:request.headers.get('Cookie'),False:"IFPToken="}[request.headers.get('Cookie') is not None]
    headers = {'Content-Type': 'application/json','Cookie': Cookie}
    query = {"query": "query me { me {user { id name username roles tenants {id name description depth isRoot} } } }",}
    r = requests.request("POST", p.IFP_DESK_API_URL, headers=headers, json=query, timeout=4, verify=p.SKIP_TLS)
    res = json.loads(r.text)
    if res.get("errors") is not None:
        query = {"query": "query me { me {user { id name username roles } } }",}
        r = requests.request("POST", p.IFP_DESK_API_URL, headers=headers, json=query, verify=p.SKIP_TLS)
        res = json.loads(r.text)

    return res

@router.post("/tenant", status_code=status.HTTP_200_OK)
async def post_tenant(*, tenantId: str = Query(...), request: Request):

    Cookie = {True:request.headers.get('Cookie'),False:"IFPToken="}[request.headers.get('Cookie') is not None]
    headers = {'Content-Type': 'application/json','Cookie': Cookie}
    reqParm = request.query_params
    query = {
        "query": "mutation setMyTenant($input: SetMyTenantInput!){setMyTenant(input: $input) {tenant {id name description depth isRoot}}}",
        "variables": {"input": {"tenantId": reqParm.get('tenantId')}},
    }
    r = requests.request("POST", p.IFP_DESK_API_URL, headers=headers, json=query, verify=p.SKIP_TLS)
    res = json.loads(r.text)
    if res.get('errors') is not None:
        raise HTTPException(status_code=401, detail=f"{res.get('errors')}")
    
    IFPTenant   = r.cookies.get_dict().get("IFPTenant")
    response = JSONResponse(content=res)
    response.set_cookie(key="IFPTenant", value=IFPTenant)

    return response
    

@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(request: Request):
    Cookie = {True:request.headers.get('Cookie'),False:"IFPToken="}[request.headers.get('Cookie') is not None]
    headers = {'Content-Type': 'application/json','Cookie': Cookie}
    query= "{\"query\":\"mutation signOut{\\r\\n  signOut\\r\\n}\",\"variables\":{}}"
    r = requests.request("POST", p.IFP_DESK_API_URL, headers=headers, data=query, verify=p.SKIP_TLS)
    res = json.loads(r.text)
    response = JSONResponse(content=res)
    response.delete_cookie("IFPToken")
    response.delete_cookie("EIToken") 
    response.delete_cookie("IFPTenant")
    return response

@services.get("/service", status_code=status.HTTP_200_OK)
def get_service_secret(*, request: Request):
    return src.getEnSaaSSecret()

@services.get("/service/ean", status_code=status.HTTP_200_OK)
def get_ean_secret(*, request: Request):
    return src.getEanSecret()

@services.get("/service/imobile", status_code=status.HTTP_200_OK)
def get_imobile_secret(*, request: Request):
    return src.getMobileSecret()

@services.get("/service/maintenance", status_code=status.HTTP_200_OK)
def get_maintenance_secret(*, request: Request):
    return src.getMaintenanceSecret()