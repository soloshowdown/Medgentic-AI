import "@/styles/globals.css";
import Layout from "@/components/Layout";
import { PredictionProvider } from "@/context/PredictionContext";

export default function App({ Component, pageProps }) {
  return (
    <PredictionProvider>
      <Layout>
        <Component {...pageProps} />
      </Layout>
    </PredictionProvider>
  );
}

