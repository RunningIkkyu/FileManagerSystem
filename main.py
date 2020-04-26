from fastapi import FastAPI, Request, Path
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from pymongo import MongoClient, DESCENDING
from pprint import pprint


app = FastAPI()
templates = Jinja2Templates(directory="templates")

mongo = MongoClient(host='47.112.210.77')
douyin_db = mongo['douyin_data']
video_collection = douyin_db['video']
video_count_each_page = 18


@app.get("/video/list/page/{page}/")
async def video_list(request: Request,
                    page:int = Path(0, title='Page of video list')):
    video_count = get_video_count()
    print(video_count)
    # If page not correct, let page equals to zero.
    if page <= 0:
        page = 0
        # Redirect
    elif page * video_count_each_page >= video_count:
        page = 0
        # Redirect
    video_list = await get_video_list(page)
    return templates.TemplateResponse(
            "index.html", 
            { "request": request, 
              "page": page,
              "video_list": video_list,
              "video_count": video_count, 
            }
         )


def get_video_count():
    video_count = video_collection.count_documents({})
    return video_count


@app.get('/api/video/page/{page}/')
async def get_video_list(
        page:int = Path(0, title='Page of video list')
        ):
    video_count = get_video_count()
    start_ind = page * video_count_each_page
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
