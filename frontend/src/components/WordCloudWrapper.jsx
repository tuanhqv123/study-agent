import React, { useMemo } from "react";

const WordCloudWrapper = ({ words }) => {
  const processedWords = useMemo(() => {
    if (!words || words.length === 0) return [];

    return words.map(({ word, count }) => ({
      text: word,
      value: count,
    }));
  }, [words]);

  if (processedWords.length === 0) {
    return (
      <div className="h-[300px] flex items-center justify-center text-muted-foreground">
        Loading word cloud...
      </div>
    );
  }

  // Simple text-based word cloud fallback
  return (
    <div className="h-[300px] p-4 flex flex-wrap items-center justify-center gap-2 overflow-hidden">
      {processedWords.slice(0, 50).map((word, index) => {
        const fontSize = Math.max(
          12,
          Math.min(
            32,
            (word.value / Math.max(...processedWords.map((w) => w.value))) *
              24 +
              12
          )
        );
        const opacity = Math.max(
          0.6,
          word.value / Math.max(...processedWords.map((w) => w.value))
        );

        return (
          <span
            key={index}
            className="inline-block px-2 py-1 rounded transition-all hover:scale-110"
            style={{
              fontSize: `${fontSize}px`,
              opacity: opacity,
              color: `hsl(${(index * 40) % 360}, 70%, 50%)`,
              fontWeight:
                word.value >
                Math.max(...processedWords.map((w) => w.value)) * 0.7
                  ? "bold"
                  : "normal",
            }}
          >
            {word.text}
          </span>
        );
      })}
    </div>
  );
};

export default WordCloudWrapper;
