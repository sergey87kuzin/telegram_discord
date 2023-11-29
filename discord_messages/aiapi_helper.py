import requests

main_url = "https://api.userapi.ai"
imagine_url = "/midjourney/v2/imagine"
account_hash = "b79727e2-842c-4a4e-a2b2-6c95a3e01400"

headers = {
    "api-key": "7e96df3f-98e2-4a37-bc30-bae2b4aa0111",
    "Content-Type": "application/json"
}


def send_imagine():
    url = main_url + imagine_url
    data = {
        "prompt": "red mushroom and a mouse",
        "webhook_url": "https://fbe66fee4b02eab1768fbad23f828928.serveo.net/api/discord_messages/discord-webhook/",
        "webhook_type": "progress",
        "account_hash": account_hash,
        "is_disable_prefilter": False
    }
    response = requests.post(url=url, json=data, headers=headers)
    print(response)
