import os

def generate_story_and_caption(client, output_dir):
    """
    Generates multiple AskReddit questions, picks the most original one,
    then writes a casual Reddit-style first-person answer.
    Returns: (story_text, caption_final, teaser_question)
    """

    # 1. Generate 3 AskReddit question candidates
    question_candidates_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You write realistic, attention-grabbing r/AskReddit questions. "
                    "They should feel like genuine Reddit questions, not clickbait headlines."
                )
            },
            {
                "role": "user",
                "content": (
                    "Generate 3 original r/AskReddit-style questions.\n\n"
                    "Rules:\n"
                    "- Each question must be max 10 words.\n"
                    "- Make them feel natural and Reddit-like.\n"
                    "- They should invite personal stories, confessions, awkward situations, or surprising real-life answers.\n"
                    "- Avoid overused templates like:\n"
                    "  'What's the biggest lie...'\n"
                    "  'When did you realize...'\n"
                    "  'How did you find out...'\n"
                    "  unless they feel genuinely fresh.\n"
                    "- Vary the topics across things like dating, marriage, breakups, money, jobs, childhood, family drama, neighbors, cheating, friendship, revenge, embarrassment, secrets, bad decisions, weird coincidences.\n"
                    "- Each question should make someone want to stop scrolling and hear the answer.\n\n"
                    "Output format:\n"
                    "1. question\n"
                    "2. question\n"
                    "3. question\n"
                    "Do not output anything else."
                )
            }
        ]
    )

    candidates_text = question_candidates_response.choices[0].message.content.strip()

    # 2. Pick the most original/best of the 3
    pick_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are selecting the best r/AskReddit question candidate."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Here are 3 AskReddit question candidates:\n\n"
                    f"{candidates_text}\n\n"
                    "Choose the SINGLE best question.\n"
                    "Pick the one that is:\n"
                    "- the most original\n"
                    "- the least repetitive or generic\n"
                    "- most likely to lead to an interesting personal story\n"
                    "- natural-sounding and Reddit-like\n\n"
                    "Output ONLY the chosen question, with no numbering or explanation."
                )
            }
        ]
    )

    teaser_question = pick_response.choices[0].message.content.strip()

    # 3. Generate a casual Reddit-style story answer
    story_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You write realistic Reddit story comments. "
                    "The stories should feel like a real person casually telling something wild that happened to them."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Question: {teaser_question}\n\n"
                    "Write a first-person Reddit-style answer to this question.\n\n"
                    "Requirements:\n"
                    "- Around 180-240 words.\n"
                    "- Sound natural, casual, and believable.\n"
                    "- The person telling the story should sound like they are just explaining what happened, not trying to sound like a movie trailer.\n"
                    "- Keep the language simple and conversational.\n"
                    "- Include a clear situation, some escalation, and an interesting reveal, conflict, or consequence.\n"
                    "- The story itself can be dramatic, awkward, messy, or shocking, but the narration should stay grounded and casual.\n"
                    "- Avoid phrases that feel overly scripted, theatrical, or suspense-baity.\n"
                    "- Do not use lines like 'you won't believe', 'that's when everything changed', 'little did I know', or similar dramatic storytelling clichés.\n"
                    "- No emojis.\n"
                    "- No hashtags.\n"
                    "- Write it as one coherent Reddit comment."
                )
            }
        ]
    )
    story_text = story_response.choices[0].message.content.strip()

    # 4. Generate hashtags
    caption_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You write short hashtag sets for social media story videos."
            },
            {
                "role": "user",
                "content": (
                    f"Based on this story and question:\n\n"
                    f"Question: {teaser_question}\n"
                    f"Story: {story_text}\n\n"
                    "Generate exactly 3 relevant hashtags.\n"
                    "- Only output hashtags\n"
                    "- Space separated\n"
                    "- No explanation"
                )
            }
        ]
    )

    extra_tags = caption_response.choices[0].message.content.strip()

    # Fixed + dynamic hashtags
    base_tags = "#reddit #askreddit #redditstories #storytime #storytelling #storyteller"
    hashtags = f"{base_tags} {extra_tags}"

    # Final caption
    caption_final = f"Part 1. {teaser_question}\n{hashtags}"

    # Save caption file
    caption_path = os.path.join(output_dir, "caption.txt")
    with open(caption_path, "w", encoding="utf-8") as f:
        f.write(caption_final)

    print(f"📝 Caption saved: {caption_path}")
    print(f"❓ Chosen question: {teaser_question}")

    return story_text, caption_final, teaser_question