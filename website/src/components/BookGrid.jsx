import BookCard from "./BookCard";

const mockBooks = [
  { title: "Pride and Prejudice", author: "Jane Austen", tags: ["Romance", "Classic"] },
  { title: "The Night Circus", author: "Erin Morgenstern", tags: ["Fantasy", "Atmospheric"] },
  { title: "The Song of Achilles", author: "Madeline Miller", tags: ["Mythology", "Tragedy"] },
];

export default function BookGrid() {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-8 mt-12 w-full max-w-6xl">
      {mockBooks.map((book, i) => (
        <BookCard key={i} {...book} />
      ))}
    </div>
  );
}
