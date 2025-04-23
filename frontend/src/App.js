import { useState } from "react";
import "./App.css";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

function App() {
  const [prompt, setPrompt] = useState("");
  const [generatedLogo, setGeneratedLogo] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handlePromptChange = (e) => {
    setPrompt(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!prompt.trim()) {
      setError("Please enter a prompt description for your logo");
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${BACKEND_URL}/api/generate-logo`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt }),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to generate logo");
      }
      
      const data = await response.json();
      setGeneratedLogo(data);
    } catch (err) {
      console.error("Error generating logo:", err);
      setError(err.message || "An error occurred while generating your logo");
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (!generatedLogo?.image) return;
    
    const link = document.createElement('a');
    link.href = `data:image/png;base64,${generatedLogo.image}`;
    link.download = `logo-${Date.now()}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-indigo-900 to-blue-900 text-white">
      <div className="container mx-auto px-4 py-12">
        <header className="text-center mb-12">
          <h1 className="text-5xl font-bold mb-4">Logo Creator</h1>
          <p className="text-xl text-blue-200">
            Generate custom logos using AI with simple text prompts
          </p>
        </header>

        <div className="max-w-3xl mx-auto bg-white/10 backdrop-blur-sm rounded-xl p-8 shadow-xl">
          <form onSubmit={handleSubmit} className="mb-8">
            <div className="mb-6">
              <label htmlFor="prompt" className="block text-lg font-medium mb-2">
                Describe your logo
              </label>
              <textarea
                id="prompt"
                value={prompt}
                onChange={handlePromptChange}
                placeholder="Describe your logo in detail (e.g., 'A modern tech company logo with blue and green elements')"
                className="w-full px-4 py-3 rounded-lg bg-white/20 backdrop-blur-sm border border-blue-300/30 text-white placeholder-blue-200/60 focus:outline-none focus:ring-2 focus:ring-blue-400"
                rows="4"
              />
              {error && <p className="mt-2 text-red-300">{error}</p>}
            </div>
            <button
              type="submit"
              disabled={loading}
              className={`w-full py-3 px-6 rounded-lg font-medium text-lg transition-all duration-300 ${
                loading
                  ? "bg-indigo-500/50 cursor-not-allowed"
                  : "bg-indigo-600 hover:bg-indigo-500"
              }`}
            >
              {loading ? "Generating..." : "Generate Logo"}
            </button>
          </form>

          {loading && (
            <div className="text-center my-12">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-300"></div>
              <p className="mt-4 text-blue-200">Creating your custom logo...</p>
            </div>
          )}

          {generatedLogo && !loading && (
            <div className="mt-8 flex flex-col items-center">
              <h2 className="text-2xl font-semibold mb-6">Your Generated Logo</h2>
              <div className="w-full max-w-md bg-white/20 backdrop-blur-sm p-4 rounded-lg shadow-lg mb-6">
                <img
                  src={`data:image/png;base64,${generatedLogo.image}`}
                  alt="Generated logo"
                  className="w-full h-auto rounded"
                />
              </div>
              <button
                onClick={handleDownload}
                className="bg-green-600 hover:bg-green-500 py-3 px-6 rounded-lg font-medium text-lg transition-all duration-300"
              >
                Download Logo
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;