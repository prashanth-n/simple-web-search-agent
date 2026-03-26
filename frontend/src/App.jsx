import Search from "./components/Search";

const appStyles = `
  :root {
    color-scheme: light;
    --background: #f4efe6;
    --surface: rgba(255, 252, 247, 0.9);
    --surface-strong: #fffaf2;
    --border: #d9c9ae;
    --text: #1f2933;
    --muted: #596579;
    --accent: #1d6f5f;
    --accent-strong: #155547;
    --shadow: 0 24px 80px rgba(43, 35, 20, 0.12);
    font-family: "Avenir Next", "Segoe UI", sans-serif;
  }

  * {
    box-sizing: border-box;
  }

  body {
    margin: 0;
    min-height: 100vh;
    background:
      radial-gradient(circle at top left, rgba(29, 111, 95, 0.12), transparent 28%),
      radial-gradient(circle at right center, rgba(193, 109, 55, 0.12), transparent 24%),
      linear-gradient(180deg, #f6f1e8 0%, #efe5d5 100%);
    color: var(--text);
  }

  a {
    color: inherit;
  }
`;

export default function App() {
  return (
    <>
      <style>{appStyles}</style>
      <Search />
    </>
  );
}
