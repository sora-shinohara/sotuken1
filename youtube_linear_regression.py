import os
import csv
from apiclient import discovery
from typing import List

# API情報
# YOUTUBE_API_KEY = 'AIzaSyDZ-k7uzmvgJ-1TklVaG1BSH0eFPJsd6RE'
YOUTUBE_API_KEY = 'AIzaSyDBIjPKCTsfGKrGd_ckJ_WA80qzzJxznNA'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

# CSV
CSV_FILE_PATH = os.path.join(os.path.dirname(__file__), "youtube.csv")
CSV_COULMN_LIST = ["video_id", "title", "published_at", "like_count",
                   "channel_id", "channel_title", "subscriber_count"]

youtube_client = discovery.build(
    YOUTUBE_API_SERVICE_NAME,
    YOUTUBE_API_VERSION,
    developerKey=YOUTUBE_API_KEY
)


class YoutubeVideoInfo:
    video_id: str
    channel_title: str
    published_at: str
    channel_id: str
    title: str
    like_count: str
    subscriber_count: str = "データ無し"


VIDEO_SEARCH_PART = 'id,snippet'
SORT_ORDER_TYPE = 'viewCount'
OUTPUT_TYPE = 'video'


def get_youtube_video_info_list(search_words: str, max_videos_count: int = 10):
    search_response = youtube_client.search().list(
        part=VIDEO_SEARCH_PART, q=search_words, order=SORT_ORDER_TYPE, type=OUTPUT_TYPE, maxResults=max_videos_count).execute()

    youtube_video_info_list = []
    for search_result in search_response.get("items", []):
        youtube_video_info = YoutubeVideoInfo()

        # Video ID ~ Channel Title まで取得
        youtube_video_info.video_id = search_result["id"]["videoId"]
        search_result_snippet = search_result["snippet"]
        youtube_video_info.title = search_result_snippet["title"]
        youtube_video_info.published_at = search_result_snippet["publishedAt"]
        youtube_video_info.channel_id = search_result_snippet["channelId"]
        youtube_video_info.channel_title = search_result_snippet["channelTitle"]

        # チャンネル登録者数を取得
        channel_statistics_response = youtube_client.channels().list(
            part='snippet,statistics',
            id=youtube_video_info.channel_id,
        ).execute()

        channel_statistics_data = channel_statistics_response[
            "items"][0]["statistics"]
        if("subscriberCount" in channel_statistics_data):
            youtube_video_info.subscriber_count = channel_statistics_data["subscriberCount"]

        # 高評価数を取得
        video_statistics_response = youtube_client.videos().list(part='snippet,statistics',
                                                                 id=youtube_video_info.video_id).execute()
        video_statistics_data = video_statistics_response["items"][0]["statistics"]
        youtube_video_info.like_count = video_statistics_data["likeCount"]

        youtube_video_info_list.append(
            youtube_video_info)
    return youtube_video_info_list


def output_to_csv(youtube_video_info_list: List[YoutubeVideoInfo]):
    with open(CSV_FILE_PATH, "w") as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(CSV_COULMN_LIST)
        for youtube_video_info in youtube_video_info_list:
            csv_writer.writerow([youtube_video_info.video_id, youtube_video_info.title, youtube_video_info.published_at, youtube_video_info.like_count,
                                youtube_video_info.channel_id, youtube_video_info.channel_title, youtube_video_info.subscriber_count])
print("a")


if __name__ == '__main__':
    youtube_video_info_list = get_youtube_video_info_list("数学")
    output_to_csv(youtube_video_info_list)
