from ..services.lmstudio_service import classify_query_lmstudio

class QueryClassifier:
    def __init__(self):
        pass

    def classify_query(self, text):
        """
        Classify the input query using LM Studio Classifier API only.
        Returns: dict with 'category', 'method', ...
        """
        if not text or text.strip() == '':
            return {
                'category': 'general',
                'method': 'empty-input'
            }
        # Gọi LM Studio Classifier API
        result = classify_query_lmstudio(text)
        # result là dict kiểu {"type": ...}
        if 'type' in result:
            return {
                'category': result['type'],
                'method': 'lmstudio'
            }
        else:
            return {
                'category': 'general',
                'method': 'lmstudio-error',
                'error': result.get('error', 'Unknown error')
            }