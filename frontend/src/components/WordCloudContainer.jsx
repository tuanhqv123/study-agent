import React, { useMemo } from "react";
import { Text } from "@visx/text";
import { scaleLog } from "@visx/scale";
import Wordcloud from "@visx/wordcloud/lib/Wordcloud";
import "./WordCloudContainer.css";

const colors = ["#143059", "#2F6B9A", "#82a6c2"];

const WordCloudContainer = ({
  words = [],
  data = [],
  width = 800,
  height = 400,
}) => {
  const processedWords = useMemo(() => {
    // Support both 'words' prop (from existing code) and 'data' prop (from new implementation)
    const sourceData = words.length > 0 ? words : data;

    if (!sourceData || sourceData.length === 0) return [];

    const processed = sourceData.map((item) => ({
      text: item.word || item.text,
      value: item.count || item.value || 1,
    }));

    return processed;
  }, [words, data]);

  const fontScale = useMemo(() => {
    if (processedWords.length === 0) return () => 10;

    const maxValue = Math.max(...processedWords.map((w) => w.value));
    const minValue = Math.min(...processedWords.map((w) => w.value));

    if (maxValue === minValue) return () => 20;

    return scaleLog({
      domain: [minValue, maxValue],
      range: [10, 60],
    });
  }, [processedWords]);

  const fontSizeSetter = (datum) => fontScale(datum.value);

  const fixedValueGenerator = () => 0.5;

  if (!processedWords || processedWords.length === 0) {
    return (
      <div className="word-cloud-container">
        <div className="word-cloud-placeholder">
          <div className="animate-spin w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full mx-auto mb-2"></div>
          <h3>Loading word cloud...</h3>
          <p>Word cloud will appear here when data is loaded</p>
        </div>
      </div>
    );
  }

  return (
    <div className="word-cloud-container">
      {" "}
      <Wordcloud
        words={processedWords}
        width={width}
        height={height}
        fontSize={fontSizeSetter}
        font={"Impact"}
        padding={1}
        spiral={"archimedean"}
        rotate={0}
        random={fixedValueGenerator}
      >
        {(cloudWords) =>
          cloudWords.map((w, i) => (
            <Text
              key={w.text}
              fill={colors[i % colors.length]}
              textAnchor={"middle"}
              transform={`translate(${w.x}, ${w.y}) rotate(${w.rotate})`}
              fontSize={w.size}
              fontFamily={w.font}
              fontWeight="900"
              style={{
                fontWeight: "900",
                textShadow: "1px 1px 2px rgba(0,0,0,0.3)",
                paintOrder: "stroke fill",
              }}
            >
              {w.text}
            </Text>
          ))
        }
      </Wordcloud>
    </div>
  );
};

export default WordCloudContainer;
