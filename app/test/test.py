from app.data.dictionaries import sensitive_words

body_text = "军刀匕首直销网10086"
for word in sensitive_words:
    if word in body_text:
        print("Request contains sensitive words")