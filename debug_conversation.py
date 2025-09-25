from supabase import create_client, Client
import json

url = "https://izhvyviovbbuiconxitm.supabase.co"
key = "sb_publishable_0K-bNGkZJiBsSMS__3AG8w_j5n-UeaX"
supabase: Client = create_client(url, key)

conversation_id = "399d996d-3400-47f9-a900-da76402c43fc"

# Check if conversation exists
conv = supabase.table('conversations').select('*').eq('id', conversation_id).execute()
print("Conversation:", json.dumps(conv.data, indent=2) if conv.data else "NOT FOUND")

if conv.data:
    deck_id = conv.data[0].get('deck_id')
    print(f"\nDeck ID: {deck_id}")
    
    # Check deck
    deck = supabase.table('uploaded_decks').select('*').eq('id', deck_id).execute()
    if deck.data:
        print(f"Deck found: {deck.data[0].get('original_filename')}")
        print(f"Extracted text exists: {deck.data[0].get('extracted_text') is not None}")
        print(f"Extracted text length: {len(deck.data[0].get('extracted_text') or '')}")
