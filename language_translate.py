def detect_language(text):
    from google.cloud import translate_v2 as translate
    
    translate_client = translate.Client()
	
    return translate_client.detect_language(text)['language']

def translate_text(target, text):
    import six
    from google.cloud import translate_v2 as translate
    translate_client = translate.Client()

    if isinstance(text, six.binary_type):
        text = text.decode('utf-8')

    result = translate_client.translate(
        text, target_language=target)

    return result['translatedText']