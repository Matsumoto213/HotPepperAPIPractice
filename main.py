import openai
import requests
import pandas as pd
import re

openai.api_key = "OPENAPI_KEY"
hotpepper_api_key = "HOTPEPPER_API_KEY"

def get_user_preferences(prompt):
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "以下の入力を解析して、ジャンル、場所、予算をそれぞれ「ジャンル:出力ジャンル 場所:出力場所 予算:出力内容（~円以内）」の改行なしの形式に分けて出力してください。"},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

def get_restaurants(api_key, genre, location, budget):
    url = "https://webservice.recruit.co.jp/hotpepper/gourmet/v1/"
    params = {
        "key": api_key,
        "format": "json",
        "genre": genre,
        "address": location,
        "budget": budget,
    }
    response = requests.get(url, params=params)
    data = response.json()
    if 'results' in data and 'shop' in data['results']:
        return data['results']['shop']
    else:
        return []

def parse_preferences(preferences):
    # 正規表現パターンを定義
    genre_pattern = re.compile(r'ジャンル:\s*([^\s]+)')
    location_pattern = re.compile(r'場所:\s*([^\s]+)')
    budget_pattern = re.compile(r'予算:\s*([^\s]+円以内)')

    # 正規表現にマッチさせて情報を抽出
    genre_match = genre_pattern.search(preferences)

    # ジャンルを正規表現で抽出
    genre = genre_match.group(1) if genre_match else None

    genre_code_map = {
        "居酒屋": "G001",
        "和食": "G004",
        "イタリアン": "G006",
    }
    genre_code = genre_code_map.get(genre)
    
    # 場所を正規表現で抽出
    location_match = location_pattern.search(preferences)
    location = location_match.group(1)
    
    # 予算を正規表現で抽出
    budget_match = budget_pattern.search(preferences)
    budget = budget_match.group(1) if budget_match else None

    budget_code_map = {
        "1000円以内": "B010",
        "2000円以内": "B001",
        "3000円以内": "B002",
    }
    budget_code = budget_code_map.get(budget)

    # print(genre_code, location, budget_code)
    return genre_code, location, budget_code

def recommend_restaurant(hotpepper_api_key, user_prompt):

    preferences = get_user_preferences(user_prompt)

    # ChatGPTの応答を解析
    genre, location, budget_code = parse_preferences(preferences)
    
    # ホットペッパーAPIからレストラン情報を取得
    restaurants = get_restaurants(hotpepper_api_key, genre, location, budget_code)
    
    # レストランのリストを生成
    if restaurants:
        recommendations = "\n".join([f"{r['name']}: {r['address']}" for r in restaurants])
    else:
        recommendations = "該当するレストランが見つかりませんでした。"

    return recommendations

def chat_with_user():
    print("こんにちは！レストランのおすすめをお手伝いします。")
    user_input = input("探している店のジャンル、場所、予算を教えてください！: ")
    recommendations = recommend_restaurant(hotpepper_api_key, user_input)
    print("おすすめのレストランはこちらです:")
    print(recommendations)

chat_with_user()