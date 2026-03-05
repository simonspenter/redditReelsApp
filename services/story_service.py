import os

def generate_story_and_caption(client, output_dir):
    """
    Generates an AskReddit question (for teaser/caption/thumbnail)
    and a first-person story-style answer.
    Returns: (story_text, caption_final, teaser_question)
    """

    # 1. Generate AskReddit question
    question_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are browsing r/AskReddit. Output ONLY the question, nothing else."},
            {"role": "user", "content": (
                "Generate a viral r/AskReddit style question.\n"
                "- Max 8 words.\n"
                "- Must be engaging, spark debate, or invite shocking answers.\n"
                "- Example: 'What secret ended up ruining someone’s life?' or 'When did you realize xxxx?' or 'How did you find out xxxx?'\n"
                "- Focus on real-life relatable topics: money, infidelity, family, friendship, work drama, revenge, secrets, regrets, childhood, morality, social norms.\n"
                "- Do NOT add quotes, punctuation around it, or extra commentary."
            )}
        ]
    )
    teaser_question = question_response.choices[0].message.content.strip()

    # 2. Generate a story as if someone is answering the question
    story_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are replying to a viral r/AskReddit question with a dramatic story."},
            {"role": "user", "content": (
                f"Question: {teaser_question}\n\n"
                "Write a dramatic Reddit-style first-person answer to this question.\n"
                "Constraints:\n"
                "- Around 200 words.\n"
                "- Conversational tone, casual but engaging.\n"
                "- Build rising tension, include a turning point in the story halfway through.\n"
                "- Then continue to finish with some resolution or twist.\n"
                "- Do not make the twist of the story too obvious by saying something like 'You'll never guess what happens next' or 'Then something amazing happened'."
                "- No emojis."
            )}
        ]
    )
    story_text = story_response.choices[0].message.content.strip()

    # 3. Generate hashtags
    caption_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You write captions for TikTok/Instagram story videos."},
            {"role": "user", "content": (
                f"From this story, create 3 relevant hashtags (ONLY hashtags, space separated)."
            )}
        ]
    )

    extra_tags = caption_response.choices[0].message.content.strip()

    # Fixed + dynamic hashtags
    base_tags = "#reddit #askreddit #redditstories #storytime #storytelling #storyteller"
    hashtags = f"{base_tags} {extra_tags}"

    # Final caption: question as teaser
    caption_final = f"Part 1. {teaser_question}\n{hashtags}"

    # Save caption file
    caption_path = os.path.join(output_dir, "caption.txt")
    with open(caption_path, "w", encoding="utf-8") as f:
        f.write(caption_final)

    print(f"📝 Caption saved: {caption_path}")

    return story_text, caption_final, teaser_question
