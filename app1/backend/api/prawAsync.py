import asyncio
import csv
import pandas as pd
import requests
import nltk
from r2 import upload, get_presigned_url
import asyncpraw
from nltk.sentiment.vader import SentimentIntensityAnalyzer

nltk.download('vader_lexicon')


def getImage(query):
    url =f"https://customsearch.googleapis.com/customsearch/v1?cx=144af1a5b59944a2b&q={query}&searchType=image&num=1&start=1&safe=off&key=AIzaSyBRlama1N7tiW0yVq45CrqCx9hyFrESmIs&alt=json"
    response = requests.get(url).json()

    return (response['items'][0]['link'])




def analyse(comm):
    analyzer = SentimentIntensityAnalyzer()
    review_segregate = {'pos_reviews': 0, 'neg_reviews': 0, 'neu_reviews': 0}
    result = {'pos': 0, 'neg': 0, 'compound': 0}
    # with open('reviews.csv', 'r' , newline="", encoding='utf-8') as csvfile:
    #     # Create a CSV reader object
    #     csvreader = csv.reader(csvfile)

        # Iterate over each row in the CSV file
    for row in comm:
            
            
            score = analyzer.polarity_scores(row)
            if score['compound'] > 0.05:
                review_segregate['pos_reviews'] += 1
            elif score['compound'] < -0.05:
                review_segregate['neg_reviews'] += 1
            else:
                review_segregate['neu_reviews'] += 1


            result['pos'] += score['pos']
            result['neg'] += score['neg']
            result['compound'] += score['compound']

            # df = pd.DataFrame(temp)
            # df.to_csv("reviews1.csv",mode='a')
        
    result['compound'] = (result['compound'] / review_segregate['neu_reviews']) * 100
    result['pos'] = (result['pos'] / review_segregate['pos_reviews']) * 100
    result['neg'] = (result['neg'] / review_segregate['neg_reviews']) * 100
        
        
    return result, review_segregate

async def get_reddit():
    reddit = asyncpraw.Reddit(
        client_id='xXMbDR-YJdPgo5opI4UPNQ',
        client_secret='kufsmFkAY_LKk0gMN_-ADr6sg5XXrA',
        user_agent="script:sentiment-analysis:v0.0.1 (by WheelLivid5381)",
        username="WheelLivid5381",
        password="Aman2004@"
    )
    # await reddit.close()
    return reddit

async def get_urls(query):
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Accept-Language": "en-IN,en-US;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br"
    }
    url = f"https://www.reddit.com/r/volvo/search.json?q={query}"
    resp = requests.get(url, headers=HEADERS).json()

    urls = []
    for url in resp['data']['children']:
        urls.append(f"https://www.reddit.com{url['data']['permalink']}")

    return urls

async def get_page(url,comm):
    reddit = await get_reddit()

    try:
        submission = await reddit.submission(url=url)
        comments = await submission.comments()
        
        for top_level_comment in comments:
            comm.append(top_level_comment.body)
    except:
        pass
    # await reddit.close()
    # with open("reviews.csv", mode='w') as csv_file:
    #     writer = csv.writer(csv_file)
        
    #     # Write each row of data to the CSV file
    #     # for row in comm:
    #     writer.writerow(comm)
    return comm

async def writedata(comm,query):
    with open(f"{query}.csv", mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        
        # Write each row of data to the CSV file
        
        writer.writerow(comm)

async def main(query):
    urls = await get_urls(query)
    # urls = ['https://www.reddit.com/r/Elphaoriondoherty/comments/148biww/tiktok_fyp_is_full_of_new_slime_pics_not_what_i/',
    #         'https://www.reddit.com/r/StardewValley/comments/y1fcq5/does_anyone_have_any_tips_for_this_quest_i_cant/',
    #         'https://www.reddit.com/r/jennymod/comments/10wj4an/is_it_possible_to_tame_slime_girls/',
    #         'https://www.reddit.com/r/LegendofSlime/comments/14ja499/whats_the_best_slime_out_right_now/']
    reddit = await get_reddit()

    tasks = []
    comm=[]
    
    for url in urls:
        print(url)

        task = asyncio.create_task(get_page(url,comm))
        tasks.append(task)

    result = await asyncio.gather(*tasks)
    # df = pd.DataFrame(result)
    # df.to_excel("reviews.xlsx")
    
    await reddit.close()
    res, seg = analyse(comm)
    await writedata(comm,query)
    upload(f"{query}.csv")
    file_dw_url = get_presigned_url(f"{query}.csv")
    print(url)
    img_url = getImage(query)
    print(res,seg)

    return res, seg, img_url,file_dw_url

if __name__ == "__main__":

    res,seg = asyncio.run(main(query="iphone 15"))
    print(res,seg)

