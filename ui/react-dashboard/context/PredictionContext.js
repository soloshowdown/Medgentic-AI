import { createContext, useContext, useState } from "react";

const PredictionContext = createContext({
  prediction: null,
  setPrediction: () => {},
});

export const PredictionProvider = ({ children }) => {
  const [prediction, setPrediction] = useState(null);

  return (
    <PredictionContext.Provider value={{ prediction, setPrediction }}>
      {children}
    </PredictionContext.Provider>
  );
};

export const usePrediction = () => useContext(PredictionContext);

