import React from "react";

const BookCard = ({ title, author, description, cover }) => {
  return (
    <div className="bg-[#F8FFFB] border border-gray-100 rounded-2xl shadow-sm hover:shadow-md transition transform hover:-translate-y-1 max-w-xs mx-auto text-center p-4">
      <img
        src={cover}
        alt={title}
        className="w-40 h-56 mx-auto rounded-lg mb-4 object-cover"
      />
      <h3 className="text-lg font-semibold text-[#4a4a4a]">{title}</h3>
      <p className="text-sm text-gray-500 mb-2">by {author}</p>
      <p className="text-gray-600 text-sm">{description}</p>
    </div>
  );
};

export default BookCard;
