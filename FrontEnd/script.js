//-------------------- Initialisation --------------------
// We are using vanilla JS to keep things simple and lightweight. No external libraries are needed for this basic functionality.
// The variables below are used to reference key elements in the DOM, such as the form, input field, submit button and result display area.
// We also define the API URL for our backend service.
const form=document.querySelector(".link-form");
const sentenceInput=document.querySelector("#analysis-sentence");
const submitButton=form?.querySelector(".form-button");
const API_URL="http://localhost:8000/process";
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
// If response is not ok, an error is thrown to be caught in the catch block of the event listener.
async function analyzeSentence(sentence) 
{
    const response=await fetch(API_URL,{
        method:"POST",
        headers:{
            "Content-Type":"application/json",
        },
        body:JSON.stringify({ text: sentence }),
    });
    if (!response.ok) {
        throw new Error("Backend request failed.");
    }
    return response.json();
}

// This function formats the analysis result received from the backend for display in the result box.
// It return either both prediction and percentage or any one or a message
// to avoid errors, we defaulty return "Analysis completed." if neither prediction nor message is present in the data.
function formatAnalysisResult(data) 
{
    if (data.prediction_message && data.confidence!==undefined) {
        const confidence=Math.round(Number(data.confidence)*100);
        return `Prediction: ${data.prediction_message} (${confidence}% confidence)`;
    }
    else if (data.prediction_message) {
        return `Prediction: ${data.prediction_message}`;
    }
    else if (data.message) {
        return data.message;
    }
    return "Analysis completed.";
}

//-------------------- Event Listeners --------------------
//Prevent default lets us handle the form submission with our custom logic instead of the browser's default behavior (which would typically involve a page reload).
//.focus() is used to set the cursor back to the input field, allowing the user to quickly correct their input without having to click back into the field.

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
        showResult(formatAnalysisResult(data), "success");
    } catch (error) {
        showResult("Unable to analyze right now.", "error");
        console.error(error);
    } finally {
        setLoading(false);
    }
});
