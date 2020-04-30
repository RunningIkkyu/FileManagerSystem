from enum import Enum
import math
import requests
from pprint import pprint

from fastapi import FastAPI, Request, Query, Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from pymongo import MongoClient, DESCENDING, ASCENDING
from pprint import pprint
from dbconfig import MONGO_CONFIG
from fastapi.staticfiles import StaticFiles
from canton_user import CANTON_USER_LIST
from not_sure_canton import NOT_SURE_CANTON_USER
from to_be_add import to_be_add_user_list


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
# app.add_template_global(get_douyin_video_link, name='get_douyin_video_link')

mongo = MongoClient(**MONGO_CONFIG)
douyin_db = mongo['douyin_data']
video_collection = douyin_db['video']
user_collection = douyin_db['user']
video_count_each_page = 24

videos_query_condition = {'user_id':{'$in': CANTON_USER_LIST}}

class VideoSortEnum(Enum):
    like_count = 'like_count'


@app.get('/vue')
async def index(request: Request):
    return templates.TemplateResponse('vue.html', {'request':request})


@app.get('/')
async def index(request: Request):
    video_count = get_video_count()
    user_count = get_user_count()
    print(video_count)
    return templates.TemplateResponse(
            "index.html", 
            { "request": request, 
              "video_count": video_count, 
              "user_count": user_count, 
            }
         )


@app.get("/videos/")
async def videos(request: Request,
                 page:int = Query(-1, title='Page of video list'),
                 cantonese:bool = Query(True, title='Filter videos of Cantonese user.'),
                 sort_by_like_count:int = Query(-1, title="Sort videos by like count."), 
                 search_by:str = Query(0, title='Search string.'),
                 search_str:str = Query('', title='Search string.'),
                 ):
    if page <= 0:
        return RedirectResponse('/videos/?page=1')
    # Redirect
    page, video_count, video_list = await get_video_list(page,
            cantonese=cantonese,
            search_by=search_by,
            sort_by_like_count=sort_by_like_count,
            search_str=search_str,
            )
    # Calculate page count.
    page_count = int(math.ceil(video_count / video_count_each_page))
    # if page > page_count:
        # return RedirectResponse('/videos/?page=0')
    # Render templates.
    return templates.TemplateResponse(
            "video_list.html", 
            { "request": request, 
              "page": page,
              "page_count": page_count,
              "video_list": video_list,
              "video_count": video_count, 
            }
         )

def get_user_count():
    count = user_collection.count_documents({})
    return count


def get_video_count(query=None):
    if query is None:
        query = {}
    video_count = video_collection.count_documents(query)
    return video_count


@app.get('/api/video/page/{page}/')
async def get_video_list(
        page: int = Path(1, title='Page of video list'),
        cantonese:bool = Query(True, title='Filter videos of Cantonese user.'),
        sort_by_like_count:int = -1,
        search_by: str = 0,
        search_str:str = '',
        ):
    query_dict = {}
    canton_list = CANTON_USER_LIST + NOT_SURE_CANTON_USER
    canton_list = to_be_add_user_list
    if search_str and int(search_by) == 0:
        query_dict = {'video_id': search_str}
    elif search_str and int(search_by) == 1:
        query_dict = {'user_name': {'$regex': f'.*{search_str}.*'}}
    elif search_str and int(search_by) == 2:
        query_dict = {'user_id': search_str}
    elif search_str and int(search_by) == 3:
        # query_dict['$text'] = {'$search': search_str}
        query_dict = {'description': {'$regex': f'.*{search_str}.*'}}
    elif cantonese:
        query_dict['user_id'] = {'$in': canton_list}
    # if search_str and int(search_by) == 2:
        # query_dict = {'video_id': video_id}

    print(search_by)
    print(search_str)
    print(query_dict)
    video_count = get_video_count(query_dict)
    # If page not correct, let page equals to zero.
    if page <= 1:
        page = 1
        # Redirect
    elif video_count - (page-1) * video_count_each_page <= 0:
        page = 1
    start_ind = (page-1) * video_count_each_page
    video_list = []
                      # .sort('like_count',DESCENDING)\
    for video_data in video_collection\
                      .find(query_dict)\
                      .sort('save_time',DESCENDING)\
                      [start_ind:start_ind+video_count_each_page]:
        #pprint(video_data)
        video_data['_id'] = str(video_data['_id'])
        video_list.append(video_data)
    return page, video_count, video_list


@app.get('/api/douyin/video/redirect_url/')
def get_douyin_video_link(url):
    headers = {
      # 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36',
      'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36',
      'Host': 'api.amemv.com',
    }
    response = requests.request("GET", url, headers=headers,allow_redirects=False)
    print(response.headers['location'])
    return response.headers['location']
    # return {'message':'success', 'url': response.headers['location']}


@app.get('/api/video/{item_id}')
async def get_video(item_id):
    ...


@app.post('/api/video/')
async def add_video():
    pass


@app.put('/api/video/')
async def update_video(video_id):
    pass


@app.delete('/api/video/')
async def delete_video():
    pass


if __name__ == "__main__":
    url = 'https://api.amemv.com/aweme/v1/play/?video_id=v0200f640000bqb6hq4lbum5k1h9clcg'
    a = get_douyin_video_link(url)
    print(a)
