import React, { useState } from "react";

// --- Our Fake Book Database ---
// We define this *outside* the component so it's not recreated on every render.
const FAKE_BOOK_DB = [
  {
    id: 1,
    title: "The Silent Garden",
    author: "L. Mayfield",
    description: "A quiet tale of love and healing in a forgotten countryside.",
    cover: "https://placehold.co/200x300/A8E6CF/333?text=The+Silent+Garden",
  },
  {
    id: 2,
    title: "Whispers of the Court",
    author: "A. Ishikawa",
    description: "A slow-burn rivalry turned romance set in an ancient kingdom.",
    cover: "https://placehold.co/200x300/A8E6CF/333?text=Whispers+of+the+Court",
  },
  {
    id: 3,
    title: "Echoes of Neon",
    author: "J. K. Vance",
    description: "A cyberpunk thriller set in the rain-slicked streets of Neo-Kyoto.",
    cover: "https://placehold.co/200x300/A8E6CF/333?text=Echoes+of+Neon",
  },
  {
    id: 4,
    title: "The Last Alchemist",
    author: "Elara Finch",
    description: "A journey to find the philosopher's stone in a world where magic is fading.",
    cover: "https://placehold.co/200x300/A8E6CF/333?text=The+Last+Alchemist",
  },
];
// --- End of Fake Database ---

// --- Updated BookCard component ---
// It now accepts a "label" prop to display a title above the card
const BookCard = ({ title, author, description, cover, label }) => (
  <div>
    {/* This is the new label */}
    {label && (
      /* --- 1. Changed text-left to text-center --- */
      <h2 className="text-xl font-semibold text-gray-800 mb-3 text-center">
        {label}
      </h2>
    )}
    <div className="bg-white rounded-lg shadow-lg overflow-hidden hover:shadow-xl transition text-left">
      <img
        src={cover}
        alt={title}
        className="w-full h-48 object-cover"
        // Add a fallback just in case
        onError={(e) => {
          e.currentTarget.src =
            "https://placehold.co/200x300/A8E6CF/333?text=Book";
        }}
      />
      <div className="p-4">
        <h3 className="text-lg font-bold text-gray-800">{title}</h3>
        <p className="text-sm text-gray-600 mb-2">{author}</p>
        <p className="text-gray-700 text-sm">{description}</p>
      </div>
    </div>
  </div>
);

const Home = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const [results, setResults] = useState([]);
  const [showResults, setShowResults] = useState(false);

  const handleSearch = () => {
    // Show the results section
    setShowResults(true);

    const query = searchQuery.toLowerCase();

    // 1. Find the searched book
    const foundBook = FAKE_BOOK_DB.find((book) =>
      book.title.toLowerCase().includes(query)
    );

    if (foundBook) {
      // 2. Find a "recommended" book (any book that is NOT the found book)
      const recommendedBook = FAKE_BOOK_DB.find(
        (book) => book.id !== foundBook.id
      );

      // 3. Set the results
      setResults([foundBook, recommendedBook]);
    } else {
      // No book was found
      setResults([]);
    }
  };

  return (
    <div className="w-full bg-gradient-to-b from-[#f6fffb] to-white px-4 pt-32 pb-20 min-h-screen">
      <div className="w-full max-w-2xl mx-auto text-center">
        {/* --- 1. Added NovelNest Title Back In --- */}
        <h1 className="text-5xl font-bold text-[#79D8B8] mb-4">NovelNest</h1>
        <p className="text-gray-600 text-lg mb-10">
          Find your next great read ✨
        </p>

        <div className="flex items-center w-full max-w-lg mx-auto bg-white rounded-full shadow-md border border-gray-200 px-4 py-2 mb-12">
          <input
            type="text"
            placeholder="Search for a book..."
            value={searchQuery} // Connect input to state
            onChange={(e) => setSearchQuery(e.target.value)} // Update state on type
            className="flex-grow outline-none text-gray-700 placeholder-gray-400 text-left"
          />
          <button
            onClick={handleSearch}
            className="bg-[#A8E6CF] hover:bg-[#93d8c0] text-gray-800 font-medium px-5 py-2 rounded-full transition"
          >
            Search
          </button>
        </div>

        {/* --- 2. Updated Results Logic --- */}
        {showResults && (
          <>
            {/* If we have results, show them */}
            {results.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* We now pass a label based on the array index */}
                {results.map((book, index) => (
                  <BookCard
                    key={book.id}
                    title={book.title}
                    author={book.author}
                    description={book.description}
                    cover={book.cover}
                    label={
                      index === 0 ? "Your Searched Book" : "Our Recommendation"
                    }
                  />
                ))}
              </div>
            ) : (
              // If we have no results, show a message
              <p className="text-gray-600">
                No results found for "{searchQuery}".
              </p>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default Home;