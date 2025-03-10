import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "./components/ui/card";
import { Button } from "./components/ui/button";
import { Input } from "./components/ui/input";
import { Search, Upload } from 'lucide-react';
import { Loader2 } from 'lucide-react';


const generateReviewTitle = (review) => {
  const words = review.toLowerCase().split(/\s+/);
  const positiveWords = ['amazing', 'excellent', 'great', 'wonderful', 'outstanding', 'fantastic', 'best', 'perfect', 'professional'];
  const procedures = ['surgery', 'treatment', 'procedure', 'experience', 'results', 'care', 'service'];
  
  const foundPositive = words.find(word => positiveWords.includes(word)) || 'Excellent';
  const foundProcedure = words.find(word => procedures.includes(word)) || 'Experience';
  
  const capitalizedPositive = foundPositive.charAt(0).toUpperCase() + foundPositive.slice(1);
  const capitalizedProcedure = foundProcedure.charAt(0).toUpperCase() + foundProcedure.slice(1);
  
  return `${capitalizedPositive} ${capitalizedProcedure} at Park Plaza Plastic Surgery`;
};

const ReviewManager = () => {
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [url, setUrl] = useState('');
  const [error, setError] = useState('');
  const [status, setStatus] = useState('');

  const scrapeReviews = async () => {
    setLoading(true);
    setError('');
    setStatus('Scraping reviews...');
    
    try {
      const response = await fetch('http://127.0.0.1:5000/api/reviews');
      const data = await response.json();
      
      if (data.success) {
        // Transform the reviews to include titles
        const reviewsWithTitles = data.reviews.map(review => ({
          ...review,
          title: generateReviewTitle(review.review),
          author: review.username,
          date: review.time_text,
          content: review.review
        }));
        
        setReviews(reviewsWithTitles);
        setStatus(`Successfully scraped ${reviewsWithTitles.length} reviews`);
      } else {
        throw new Error(data.error || 'Failed to scrape reviews');
      }
    } catch (err) {
      setError('Error scraping reviews: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const uploadReviews = async () => {
    setUploading(true);
    setError('');
    
    try {
      // Make POST request to your WordPress upload endpoint
      const response = await fetch('http://127.0.0.1:5000/api/upload', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ reviews }),
      });
      
      const data = await response.json();
      
      if (data.success) {
        setStatus('Successfully uploaded all reviews!');
      } else {
        throw new Error(data.error || 'Failed to upload reviews');
      }
    } catch (err) {
      setError('Error uploading reviews: ' + err.message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-6">
      <Card className="w-full max-w-4xl bg-white rounded-3xl shadow-none">
        <CardContent className="p-8">
          <h2 className="text-2xl font-semibold my-6">Review Manager</h2>
          
          <div className="space-y-6">
            {/* URL Input Section */}
            <div className="flex gap-4">
              <Input 
                type="text" 
                placeholder="Enter Google Reviews URL" 
                className="flex-1 border border-gray-200 bg-white shadow-sm rounded-2xl h-12"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
              />
              <Button 
                className="bg-gray-900 text-white hover:bg-gray-800 shadow-none rounded-2xl h-12 px-6"
                onClick={scrapeReviews}
                disabled={loading}
              >
                {loading ? (
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                ) : (
                  <Search className="w-4 h-4 mr-2" />
                )}
                {loading ? 'Scraping...' : 'Scrape Reviews'}
              </Button>
            </div>

            {/* Status Messages */}
            {error && (
              <div className="bg-red-50 text-red-500 p-4 rounded-2xl">
                {error}
              </div>
            )}
            
            {status && !error && (
              <div className="bg-blue-50 text-blue-500 p-4 rounded-2xl">
                {status}
              </div>
            )}

            {/* Reviews Section */}
            {reviews.length > 0 && (
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <h3 className="text-xl font-semibold">
                    Scraped Reviews ({reviews.length})
                  </h3>
                  <Button 
                    className="bg-gray-900 text-white hover:bg-gray-800 shadow-none rounded-2xl h-12 px-6"
                    onClick={uploadReviews}
                    disabled={uploading || reviews.length === 0}
                  >
                    {uploading ? (
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    ) : null}
                    {uploading ? 'Uploading...' : 'Upload All Reviews'}
                  </Button>
                </div>

                {/* Review Cards */}
                <div className="space-y-4">
                  {reviews.map((review, index) => (
                    <div key={index} className="border border-gray-200 rounded-3xl p-6 bg-white">
                      <h4 className="text-xl font-semibold mb-2">{review.title}</h4>
                      <div className="text-gray-500 mb-3">
                        By {review.author} • {review.date}
                      </div>
                      <p className="text-gray-800 text-lg">{review.content}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ReviewManager;