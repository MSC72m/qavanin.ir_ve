import requests
import re
import pythonmonkey as pm
import os
import aiohttp

BASE_URL: str = "https://qavanin.ir/"
BASE_QAVANIN_URL: str = f"{BASE_URL}/Law/TreeText/?IDS="
URL_TEMPLATE: str = (
    "https://qavanin.ir/?CAPTION=&Zone=&IsTitleSearch=true&IsTitleSearch=false&IsTextSearch=false&_isLaw=false&_isRegulation=false&_IsVote=false&_isOpenion=false&SeachTextType=3&fromApproveDate=&APPROVEDATE=&IsTitleSubject=False&IsMain=&COMMANDNO=&fromCommandDate=&COMMANDDATE=&NEWSPAPERNO=&fromNewspaperDate=&NEWSPAPERDATE=&SortColumn=APPROVEDATE&SortDesc=True&Report_ID=&PageNumber={page}&page={page}&size=1000&txtZone=&txtSubjects=&txtExecutors=&txtApprovers=&txtLawStatus=&txtLawTypes="
)
CDN_REGEX: str = r"<\/script><script type=\"text\/javascript\">(var.+\n)"

if not os.path.exists("./files/pages"):
    os.makedirs("./files/pages")

if not os.path.exists("./files/qavanin"):
    os.makedirs("./files/qavanin")


def get_hash(content: str) -> str:
    func = "(function() {return hash})();"
    matches = re.findall(CDN_REGEX, content)
    if len(matches) == 0:
        return None
    js = matches[0]
    js_code = f"{js}\n{func}"
    res = pm.eval(js_code)
    return res


def get_page(url, headers={}, payload={}):
    response = requests.request("GET", url, headers=headers, data=payload)
    return response.text



async def get_page_async(url: str, headers: dict = {}, payload: dict = {}) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, data=payload) as response:
            return await response.text()


