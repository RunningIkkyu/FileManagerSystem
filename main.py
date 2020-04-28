from enum import Enum

from fastapi import FastAPI, Request, Query, Path
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from pymongo import MongoClient, DESCENDING
from pprint import pprint
from dbconfig import MONGO_CONFIG
from fastapi.staticfiles import StaticFiles



app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

mongo = MongoClient(**MONGO_CONFIG)
douyin_db = mongo['douyin_data']
video_collection = douyin_db['video']
user_collection = douyin_db['user']
video_count_each_page = 24


class VideoSortEnum(Enum):
    like_count = 'like_count'


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
                 page:int = Query(1, title='Page of video list'),
                 sort:VideoSortEnum = Query('like_count', title='sort method'),
                 ):
    video_count = get_video_count()
    print(video_count)
    # If page not correct, let page equals to zero.
    if page <= 1:
        page = 1
        # Redirect
    elif page * video_count_each_page >= video_count:
        page = 1
        # Redirect
    video_list = await get_video_list(page)
    return templates.TemplateResponse(
            "video_list.html", 
            { "request": request, 
              "page": page,
              "video_list": video_list,
              "video_count": video_count, 
            }
         )

def get_user_count():
    count = user_collection.count_documents({})
    return count

def get_video_count():
    video_count = video_collection.count_documents({})
    return video_count

def get_video_count():
    video_count = video_collection.count_documents({})
    return video_count


@app.get('/api/video/page/{page}/')
async def get_video_list(
        page:int = Path(1, title='Page of video list')
        ):
    video_count = get_video_count()
    start_ind = (page-1) * video_count_each_page
    video_list = []
    for video_data in video_collection\
                      .find()\
                      .sort('like_count',DESCENDING)\
                      [start_ind:start_ind+video_count_each_page]:
        #pprint(video_data)
        video_data['_id'] = str(video_data['_id'])
        video_list.append(video_data)
    return video_list


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
