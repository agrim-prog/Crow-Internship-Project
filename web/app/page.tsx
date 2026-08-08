import Header from "@/components/Header";
import Hero from "@/components/Hero";
import StepsSection from "@/components/StepsSection";
import Workbench from "@/components/Workbench";
import Footer from "@/components/Footer";

export default function Home() {
  return (
    <>
      <Header />
      <main>
        <Hero />
        <StepsSection />
        <Workbench />
      </main>
      <Footer />
    </>
  );
}
