# Rule: Save to Obsidian Trigger

Whenever the user inputs the phrase **"Save to Obsidian"** (or variations like "save chat to obsidian"), automatically perform the following actions:

1. **Target Folder**: `/Users/a1/Documents/Second Brain/Second Brain/02 My Businesses`
2. **File Creation & Naming Strategy**:
   - **Default (New Note Per Session)**: Create a new note for each chat session named `YYYY-MM-DD - [Main Topic] Chat Summary.md` (or `YYYY-MM-DD-HHmm - [Main Topic].md` if multiple sessions occur on the same day).
   - **Re-runs within the same chat session**: If "Save to Obsidian" is called multiple times within the *same active chat*, update/overwrite the current session's note with the updated full transcript summary.
3. **Summary Formatting**:
   - Format specifically for **Obsidian Second Brain**:
     - **YAML Frontmatter**: Includes `tags: [chat-summary, project/ai-agent, business/02]`, `date`, `summary_type: session-digest`, `status: completed`.
     - **Callouts**: Use Obsidian callouts like `> [!summary]`, `> [!info]`, `> [!todo]`, `> [!key-takeaways]`.
     - **WikiLinks**: Use `[[...]]` links for topics and related notes.
     - **Mermaid Diagrams**: Include flow diagrams where relevant.
4. **User Output**:
   - Confirm completion and provide a direct `file://` link to the saved Obsidian note.
