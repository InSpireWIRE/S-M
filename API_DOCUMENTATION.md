# S!M API Endpoints

## POST /api/upload-deck
- Accepts: PDF file via multipart/form-data
- Returns: {conversation_id: "uuid"}

## POST /api/start-conversation  
- Accepts: {conversation_id: "uuid"}
- Returns: {question: "first question text"}

## POST /api/submit-answer
- Accepts: {conversation_id: "uuid", question_number: int, answer_text: "string"}
- Returns: {next_question: "string"} OR {conversation_complete: true, synthesis: "full synthesis text"}

## GET /api/status
- Returns: {"status": "S!M Backend Running with Sophisticated Chunking"}
