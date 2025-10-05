AI Prompts Documentation
1. Purpose

The AI functionality in the Notes App is designed to automatically generate summaries for user-created notes. This helps users quickly review the content of their notes without reading the entire text.

2. AI Tool Used

Gemini CLI: The AI engine is invoked via a command-line interface (subprocess.run) from Python.

Input: The text content of the note.

Output: A concise summary of the note content.

3. Prompt Structure

When creating a note, the backend constructs a prompt for the AI:

Summarize the following text: <note content>


<note content> is dynamically replaced with the actual content of the user’s note.

Optional post-processing truncates very long summaries to a maximum of 200 characters with ellipsis (...).

4. Implementation Workflow

User creates a note via the frontend (title, content, category, pinned).

Backend receives the note content via /notes POST request.

Backend calls the generate_summary function.

generate_summary runs the Gemini CLI with the prompt:

cmd = f'gemini "Summarize the following text: {note_content}"'
result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)


If successful, the summary is saved in the database along with the note.

The frontend displays the summary (if available) under each note.

5. Example

Note Content:

Today I studied Flask and learned how to integrate JWT authentication, create REST APIs, and deploy the app on Render.com.


AI Prompt Sent to Gemini:

Summarize the following text: Today I studied Flask and learned how to integrate JWT authentication, create REST APIs, and deploy the app on Render.com.


Generated Summary:

Studied Flask: JWT authentication, REST APIs, and deployment on Render.com.

6. Notes and Limitations

AI summarization is optional; if the Gemini CLI fails, the note is still saved with summary set to "Summary could not be generated."

Summaries are truncated to avoid overly long texts in the UI.

The AI is called synchronously during note creation, so very large notes may slightly delay response time.