'use client';
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { fastApiClient } from "@/lib/api";
import { Separator } from "@radix-ui/react-separator";
import { useState } from "react";
import ReactMarkdown from 'react-markdown';

export default function Home() {
  const [text, setText] = useState("");
  const [textResponse, setTextResponse] = useState("");
  const [loading, setLoading] = useState(false);

  const callAPI = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await fastApiClient.get(`/api/gen/correct?text=${text}`);
      console.log(response);
      setTextResponse(response.data.corrected_text);
    } catch (error) {
      console.error("Error calling API:", error);
      setTextResponse("Error: " + (error.message || "Something went wrong"));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col items-center justify-center p-4 min-h-screen bg-gray-100">
      <Card className="w-full max-w-3xl shadow-lg">
        <CardHeader>
          <CardTitle>Correct the English text</CardTitle>
          <CardDescription>
            Enter your English text below to check for grammar and spelling errors
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-col space-y-4">
            <div className="space-y-2">
              <label htmlFor="input-text" className="text-sm font-medium">Input Text</label>
              <Textarea 
                id="input-text"
                placeholder="Type or paste your text here..." 
                value={text} 
                onChange={(e) => setText(e.target.value)}
                className="min-h-[120px] max-h-[300px] overflow-y-auto"
              />
            </div>
            
            <Button 
              onClick={callAPI} 
              disabled={loading || !text.trim()}
              className="w-full"
            >
              {loading ? "Correcting..." : "Correct Text"}
            </Button>
            
            <Separator className="my-4" />
            
            <div className="space-y-2">
              <label htmlFor="output-text" className="text-sm font-medium">Corrected Text</label>
              <div 
                id="output-text"
                className="border rounded-md p-4 min-h-[120px] max-h-[300px] overflow-y-auto bg-gray-50 prose prose-sm max-w-none"
              >
                {textResponse ? (
                  <ReactMarkdown>{textResponse}</ReactMarkdown>
                ) : (
                  <span className="text-gray-400 italic">
                    Corrected text will appear here...
                  </span>
                )}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
