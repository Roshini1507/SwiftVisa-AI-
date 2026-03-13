from duckduckgo_search import DDGS


def search_web(query):

    try:
        results_text = []

        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=5)

            for r in results:
                results_text.append(r["body"])

        return "\n".join(results_text)

    except Exception as e:
        print("Web search error:", e)
        return ""