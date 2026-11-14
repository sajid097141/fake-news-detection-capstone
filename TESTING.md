# VERITAS — Testing Guide

## 1. Test framework

The automated test suite uses Python's built-in `unittest` framework and `unittest.mock`. External HTTP services are mocked so tests do not consume API quota or depend on live Google Fact Check Tools or GDELT availability.

## 2. Run the tests

From the repository root:

```bash
python -m unittest discover -s tests -v
```

## 3. Test coverage

The suite covers the Flask API and external-service client error handling.

### API tests

- Health endpoint response.
- Non-JSON and non-object JSON requests.
- Incorrect headline/article field types.
- Missing and too-short article text.
- Oversized headline and article inputs.
- Successful unified analysis with all three result streams.
- GDELT failure while preserving the ML and fact-check results.
- Fact-check API failure while preserving the ML and news-coverage results.
- Both external services unavailable while preserving the ML result.
- ML model failure handling.
- Legacy `/api/predict` endpoint compatibility.
- Invalid input to the legacy and standalone evidence endpoints.

### External-client tests

- GDELT HTTP 429 rate-limit handling.
- GDELT non-JSON response handling.
- GDELT empty article-list handling.
- GDELT empty-query validation.
- Fact-check HTTP error handling without exposing the API key.
- Fact-check invalid-JSON handling.
- Empty claim handling in the relevance filter.

## 4. Recorded local test run

The project test run reported by the developer during the VERITAS 2.0 workflow:

```text
Ran 24 tests
OK
```

This is a recorded local result, not a claim that tests have been run in every environment or on every future commit. Run the command above again after pulling changes or modifying dependencies.

## 5. Manual browser checks

After starting the Flask app:

1. Open `http://127.0.0.1:5000`.
2. Confirm the page loads and the browser console has no application errors.
3. Submit a headline and a sufficiently long article.
4. Confirm the ML prediction is displayed.
5. Confirm fact-check and news-coverage panels show results or a clear unavailable state.
6. Confirm that an external-service failure does not hide a successful ML prediction.
7. Confirm the disclaimer and privacy notice remain visible.

A missing `/favicon.ico` may produce a 404 if no favicon is configured. This does not by itself indicate a failure in the application routes or analysis workflow.

## 6. Live-service considerations

Live API behaviour can differ from mocked test behaviour. Google Fact Check Tools results depend on available published reviews. GDELT may return no matching articles or may apply rate limits (HTTP 429). These conditions are expected to be handled as unavailable evidence in unified analysis rather than as a failure of the local model.

## 7. Environment note

Use the Python version and pinned model dependencies specified by the project. Before deployment or merging, activate the project's virtual environment, install the complete requirements, and rerun the test suite in that environment.
