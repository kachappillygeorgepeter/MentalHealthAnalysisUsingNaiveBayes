//-------------------- Initialisation --------------------
// We are using vanilla JS to keep things simple and lightweight. No external libraries are needed for this basic functionality.
// The variables below are used to reference key elements in the DOM, such as the form, input field, submit button and result display area.
// We also define the API URL for our backend service.
const form=document.querySelector(".link-form");
const sentenceInput=document.querySelector("#analysis-sentence");
const submitButton=form?.querySelector(".form-button");
const API_BASE = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
    ? "http://127.0.0.1:8000"
    : "https://mental-health-analysis-using-naive.vercel.app";
const API_URL = `${API_BASE}/process`;
const RANDOM_SENTENCE_URL = `${API_BASE}/random-sentence`;
const resultBox=document.querySelector(".analysis-result");
// Function is used to display messages in the result box. 
// It accepts a message and an optional type parameter to indicate the nature of the message (e.g., info, success, error).
function showResult(message, type="info") 
{
    resultBox.textContent=message;
    resultBox.dataset.type=type;
}

// This function is used to toggle the loading state of the submit button. 
// When isLoading is true, the button is disabled and its text changes to "Analyzing...". 
// When false, the button is enabled and its text reverts to "Analyze Sentence".
// If statement is used to check if the submitButton exists before trying to modify it, preventing potential errors if the element is not found in the DOM.
function setLoading(isLoading) 
{
    if (!submitButton) {
        return;
    }
    submitButton.disabled=isLoading;
    submitButton.textContent=isLoading?"Analyzing...":"Analyze Sentence";
}

// Send the sentence to the backend server and receive the analysis result
// fetch gets data by default, using POST ensures sending data
// Headers specify that the content type is JSON and the body contains the sentence to be analyzed, also in JSON format.
// If the backend returns 503 (API issue), throw a special MaintenanceError so the caller can show the maintenance screen.
async function analyzeSentence(sentence) 
{
    const response=await fetch(API_URL,{
        method:"POST",
        headers:{
            "Content-Type":"application/json",
        },
        body:JSON.stringify({ text: sentence }),
    });

    const responseData = await response.json().catch(() => null);

    if (response.status === 503) {
        // API is having issues — log the full details to the browser console.
        const detail = responseData?.detail || {};
        console.error(
            "%c⚠ GEMINI API ISSUE DETECTED",
            "color: #ff6b6b; font-size: 14px; font-weight: bold;"
        );
        console.error("Error Type :", detail.error_type  || "Unknown");
        console.error("API Error  :", detail.api_error   || "No details returned.");
        console.error("Full detail:", detail);
        // Throw a typed error so the form handler shows "SERVER UNDER MAINTAINENCE"
        const err = new Error("SERVER_UNDER_MAINTENANCE");
        err.isApiMaintenance = true;
        throw err;
    }

    if (!response.ok) {
        const detail = responseData?.detail?.message || responseData?.detail || response.statusText;
        throw new Error(`Backend request failed with status ${response.status}: ${detail}`);
    }

    return responseData;
}


// This function formats the analysis result received from the backend for display in the result box.
// It return either both prediction and percentage or any one or a message
// to avoid errors, we defaulty return "Analysis completed." if neither prediction nor message is present in the data.
function formatAnalysisResult(data) 
{
    if (data.prediction_message && data.confidence!==undefined) {
        const confidence=Math.round(Number(data.confidence)*100);
        return `Predicted Emotion: ${data.prediction_message.charAt(0).toUpperCase() + data.prediction_message.slice(1)} (${confidence}% confidence)`;
    }
    else if (data.prediction_message) {
        return `Predicted Emotion: ${data.prediction_message.charAt(0).toUpperCase() + data.prediction_message.slice(1)}`;
    }
    else if (data.message) {
        return data.message;
    }
    return "Analysis completed.";
}

//-------------------- Event Listeners --------------------
//Prevent default lets us handle the form submission with our custom logic instead of the browser's default behavior (which would typically involve a page reload).
//.focus() is used to set the cursor back to the input field, allowing the user to quickly correct their input without having to click back into the field.

const charCountSpan = document.querySelector("#char-count");

function updateCharCount() {
    if (sentenceInput && charCountSpan) {
        charCountSpan.textContent = sentenceInput.value.length;
    }
}

sentenceInput?.addEventListener("input", updateCharCount);

const sampleButtons = document.querySelectorAll(".sample-btn");
sampleButtons.forEach(btn => {
    btn.addEventListener("click", async () => {
        if (!sentenceInput) return;
        const emotion = btn.dataset.emotion;
        if (!emotion) return;

        const originalText = btn.textContent;
        try {
            btn.disabled = true;
            btn.textContent = "Loading...";
            
            const response = await fetch(`${RANDOM_SENTENCE_URL}?emotion=${emotion}`);
            if (!response.ok) {
                throw new Error("Failed to fetch sentence");
            }
            const data = await response.json();
            if (data && data.sentence) {
                sentenceInput.value = data.sentence;
                updateCharCount();
                sentenceInput.focus();
            }
        } catch (error) {
            console.error("Error fetching random sentence:", error);
            showResult("Failed to fetch a random sentence. Please try again or start the backend locally.", "error");
        } finally {
            btn.disabled = false;
            btn.textContent = originalText;
        }
    });
});

form?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const sentence=sentenceInput.value.trim();
    if (!sentence) {
        showResult("Please enter a sentence before analyzing.", "error");
        sentenceInput.focus();
        return;
    }
//-------------------- Code Start --------------------
    try {
        setLoading(true);
        showResult("Analyzing sentence...", "loading");
        const data=await analyzeSentence(sentence);

        // If the backend used local Naive Bayes logic, log it to the browser console too.
        if (!data.chatbot_used) {
            console.log(
                "%c[LOCAL PREDICTION]",
                "color: #4caf50; font-weight: bold;",
                `Emotion: ${data.prediction_message?.toUpperCase()}`,
                `| Confidence: ${Math.round(Number(data.confidence) * 100)}%`,
                `| Filtered text: "${data.filtered_text}"`
            );
        }

        showResult(formatAnalysisResult(data), "success");
    } catch (error) {
        if (error.isApiMaintenance) {
            // API quota/key/network failure — tell the user and the console
            console.error(
                "%c🔧 SERVER UNDER MAINTAINENCE — Gemini API is currently unavailable.",
                "color: #ff6b6b; font-weight: bold; font-size: 13px;"
            );
            showResult("🔧 SERVER UNDER MAINTAINENCE", "error");
        } else {
            showResult("Unable to analyze right now. Start the backend with: py -m uvicorn main:app --reload, then check /health.", "error");
            console.error(error);
        }
    } finally {
        setLoading(false);
    }
});

