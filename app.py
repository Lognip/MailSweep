from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/cleanup_emails', methods=['POST'])
def cleanup_emails():
    data = request.json
    access_token = data.get("access_token")

    if not access_token:
        return jsonify({"error": "Missing access token"}), 400

    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    graph_url = "https://graph.microsoft.com/v1.0/me/messages"
    
    response = requests.get(graph_url, headers=headers)
    if response.status_code != 200:
        return jsonify({"error": "Failed to retrieve emails", "details": response.json()}), 400

    emails = response.json().get("value", [])
    conversation_dict = {}

    for email in emails:
        conv_id = email.get("conversationId")
        email_id = email.get("id")
        if not conv_id or not email_id:
            continue

        if conv_id in conversation_dict:
            delete_url = f"https://graph.microsoft.com/v1.0/me/messages/{email_id}"
            delete_response = requests.delete(delete_url, headers=headers)

            if delete_response.status_code == 204:
                print(f"🗑 Deleted old email: {email.get('subject', 'Unknown subject')}")
            else:
                print(f"❌ Failed to delete email: {delete_response.json()}")
        else:
            conversation_dict[conv_id] = email  # Keep the latest email

    return jsonify({"message": "✅ Old emails removed, latest emails retained!"})

if __name__ == "__main__":
    app.run(debug=True)
