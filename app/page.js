import ButtonGradient from "@/components/svg/ButtonGradient";
// import Stats from "@/components/stats";
import Benefits from "@/components/Benefits";
import Collaboration from "@/components/Collaboration";
import Header from "@/components/Header";
import Hero from "@/components/Hero";
import Services from "@/components/Services";
import Pricing from "@/components/Pricing";
import Footer from "@/components/Footer";
import Whychoose from "@/components/whychoose";
import AnimatedTestimonials from "@/components/testimonial";

export default function Home() {
  return (
    <main className="relative w-full overflow-hidden">
      <div className="flex flex-col min-h-screen">
        <Header />
        <Hero />
        <Benefits />
        <Collaboration />
        <Services />
        <Whychoose />
        <Pricing />
        <AnimatedTestimonials />
        <Footer />
      </div>
      
      {/* Position ButtonGradient absolutely to prevent layout shifts */}
      <div className="fixed inset-0 pointer-events-none">
        <ButtonGradient />
      </div>
    </main>
  );
}

