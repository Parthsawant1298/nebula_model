import { useEffect, useState } from "react";
import { MouseParallax } from "react-just-parallax";

const PlusSvg = ({ className = "" }) => {
  return (
    <svg className={`${className} || ""`} width="11" height="11" fill="none">
      <path
        d="M7 1a1 1 0 0 0-1-1H5a1 1 0 0 0-1 1v2a1 1 0 0 1-1 1H1a1 1 0 0 0-1 1v1a1 1 0 0 0 1 1h2a1 1 0 0 1 1 1v2a1 1 0 0 0 1 1h1a1 1 0 0 0 1-1V8a1 1 0 0 1 1-1h2a1 1 0 0 0 1-1V5a1 1 0 0 0-1-1H8a1 1 0 0 1-1-1V1z"
        fill="#ada8c4"
      />
    </svg>
  );
};

export const Gradient = () => (
  <>
    <div className="relative z-1 h-4 mx-2 sm:h-5 sm:mx-4 lg:h-6 lg:mx-8 bg-n-11 shadow-xl rounded-b-[1rem] lg:rounded-b-[1.25rem]" />
    <div className="relative z-1 h-4 mx-4 sm:h-5 sm:mx-8 lg:h-6 lg:mx-20 bg-n-11/70 shadow-xl rounded-b-[1rem] lg:rounded-b-[1.25rem]" />
  </>
);

export const BottomLine = () => (
  <>
    <div className="hidden lg:block absolute top-[40rem] xl:top-[55.25rem] left-10 right-10 h-0.25 bg-n-6 pointer-events-none" />
    <PlusSvg className="hidden lg:block absolute top-[39.75rem] xl:top-[54.9375rem] left-[2.1875rem] z-2 pointer-events-none" />
    <PlusSvg className="hidden lg:block absolute top-[39.75rem] xl:top-[54.9375rem] right-[2.1875rem] z-2 pointer-events-none" />
  </>
);

export const BackgroundCircles = ({ parallaxRef }) => {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <div className="absolute -top-[20rem] sm:-top-[28rem] md:-top-[32rem] xl:-top-[32rem] left-1/2 w-[90vw] sm:w-[35rem] lg:w-[65rem] aspect-square -translate-x-1/2">
      <MouseParallax strength={0.08} parallaxContainerRef={parallaxRef}>
        {/* Original circles */}
        <div className="absolute bottom-1/2 left-1/2 w-0.25 h-1/2 origin-bottom rotate-[46deg]">
          <div
            className={`w-2.5 h-2.5 sm:w-3 sm:h-3 -ml-1 -mt-20 sm:-mt-36 bg-gradient-to-b from-[#DD734F]/70 to-[#1A1A32]/70 rounded-full transition-transform duration-500 ease-out ${
              mounted ? "translate-y-0 opacity-70" : "translate-y-10 opacity-0"
            }`}
          />
        </div>

        <div className="absolute bottom-1/2 left-1/2 w-0.25 h-1/2 origin-bottom -rotate-[56deg]">
          <div
            className={`w-3 h-3 sm:w-4 sm:h-4 -ml-1 -mt-16 sm:-mt-32 bg-gradient-to-b from-[#DD734F]/70 to-[#1A1A32]/70 rounded-full transition-transform duration-500 ease-out ${
              mounted ? "translate-y-0 opacity-70" : "translate-y-10 opacity-0"
            }`}
          />
        </div>

        <div className="absolute bottom-1/2 left-1/2 w-0.25 h-1/2 origin-bottom rotate-[54deg]">
          <div
            className={`hidden lg:block w-4 h-4 -ml-1 mt-[12.9rem] bg-gradient-to-b from-[#B9AEDF]/70 to-[#1A1A32]/70 rounded-full transition-transform duration-500 ease-out ${
              mounted ? "translate-y-0 opacity-70" : "translate-y-10 opacity-0"
            }`}
          />
        </div>

        <div className="absolute bottom-1/2 left-1/2 w-0.25 h-1/2 origin-bottom -rotate-[65deg]">
          <div
            className={`w-3 h-3 sm:w-4 sm:h-4 -ml-1.5 mt-32 sm:mt-52 bg-gradient-to-b from-[#B9AEDF]/70 to-[#1A1A32]/70 rounded-full transition-transform duration-500 ease-out ${
              mounted ? "translate-y-0 opacity-70" : "translate-y-10 opacity-0"
            }`}
          />
        </div>

        <div className="absolute bottom-1/2 left-1/2 w-0.25 h-1/2 origin-bottom -rotate-[85deg]">
          <div
            className={`w-4 h-4 sm:w-5 sm:h-5 -ml-2 sm:-ml-2.5 -mt-2 sm:-mt-2.5 bg-gradient-to-b from-[#88E5BE]/70 to-[#1A1A32]/70 rounded-full transition-transform duration-500 ease-out ${
              mounted ? "translate-y-0 opacity-70" : "translate-y-10 opacity-0"
            }`}
          />
        </div>

        <div className="absolute bottom-1/2 left-1/2 w-0.25 h-1/2 origin-bottom rotate-[70deg]">
          <div
            className={`w-4 h-4 sm:w-5 sm:h-5 -ml-2 sm:-ml-2.5 -mt-2 sm:-mt-2.5 bg-gradient-to-b from-[#88E5BE]/70 to-[#1A1A32]/70 rounded-full transition-transform duration-500 ease-out ${
              mounted ? "translate-y-0 opacity-70" : "translate-y-10 opacity-0"
            }`}
          />
        </div>

        {/* Additional circles */}
        <div className="absolute bottom-1/2 left-1/2 w-0.25 h-1/2 origin-bottom rotate-[30deg]">
          <div
            className={`w-3 h-3 sm:w-4 sm:h-4 -ml-1.5 -mt-24 sm:-mt-40 bg-gradient-to-b from-[#FF9F7A]/70 to-[#1A1A32]/70 rounded-full transition-transform duration-500 ease-out ${
              mounted ? "translate-y-0 opacity-70" : "translate-y-10 opacity-0"
            }`}
          />
        </div>

        <div className="absolute bottom-1/2 left-1/2 w-0.25 h-1/2 origin-bottom -rotate-[40deg]">
          <div
            className={`w-5 h-5 sm:w-6 sm:h-6 -ml-3 -mt-12 sm:-mt-28 bg-gradient-to-b from-[#DD734F]/70 to-[#1A1A32]/70 rounded-full transition-transform duration-500 ease-out ${
              mounted ? "translate-y-0 opacity-70" : "translate-y-10 opacity-0"
            }`}
          />
        </div>

        {/* <div className="absolute bottom-1/2 left-1/2 w-0.25 h-1/2 origin-bottom rotate-[15deg]">
          <div
            className={`w-4 h-4 sm:w-5 sm:h-5 -ml-2 mt-20 sm:mt-36 bg-gradient-to-b from-[#C7B8FF]/70 to-[#1A1A32]/70 rounded-full transition-transform duration-500 ease-out ${
              mounted ? "translate-y-0 opacity-70" : "translate-y-10 opacity-0"
            }`}
          />
        </div>

        <div className="absolute bottom-1/2 left-1/2 w-0.25 h-1/2 origin-bottom -rotate-[25deg]">
          <div
            className={`w-6 h-6 sm:w-7 sm:h-7 -ml-3 mt-10 sm:mt-24 bg-gradient-to-b from-[#B9AEDF]/70 to-[#1A1A32]/70 rounded-full transition-transform duration-500 ease-out ${
              mounted ? "translate-y-0 opacity-70" : "translate-y-10 opacity-0"
            }`}
          />
        </div>

        <div className="absolute bottom-1/2 left-1/2 w-0.25 h-1/2 origin-bottom rotate-[85deg]">
          <div
            className={`w-3 h-3 sm:w-4 sm:h-4 -ml-1.5 mt-8 sm:mt-16 bg-gradient-to-b from-[#7DEBB1]/70 to-[#1A1A32]/70 rounded-full transition-transform duration-500 ease-out ${
              mounted ? "translate-y-0 opacity-70" : "translate-y-10 opacity-0"
            }`}
          />
        </div> */}

        <div className="absolute bottom-1/2 left-1/2 w-0.25 h-1/2 origin-bottom -rotate-[75deg]">
          <div
            className={`w-5 h-5 sm:w-6 sm:h-6 -ml-2.5 mt-16 sm:mt-28 bg-gradient-to-b from-[#88E5BE]/70 to-[#1A1A32]/70 rounded-full transition-transform duration-500 ease-out ${
              mounted ? "translate-y-0 opacity-70" : "translate-y-10 opacity-0"
            }`}
          />
        </div>

        <div className="absolute bottom-1/2 left-1/2 w-0.25 h-1/2 origin-bottom rotate-[100deg]">
          <div
            className={`w-4 h-4 sm:w-5 sm:h-5 -ml-2 -mt-16 sm:-mt-24 bg-gradient-to-b from-[#94E9D0]/70 to-[#1A1A32]/70 rounded-full transition-transform duration-500 ease-out ${
              mounted ? "translate-y-0 opacity-70" : "translate-y-10 opacity-0"
            }`}
          />
        </div>

        <div className="absolute bottom-1/2 left-1/2 w-0.25 h-1/2 origin-bottom -rotate-[100deg]">
          <div
            className={`w-3 h-3 sm:w-4 sm:h-4 -ml-1.5 -mt-14 sm:-mt-20 bg-gradient-to-b from-[#6FCCAA]/70 to-[#1A1A32]/70 rounded-full transition-transform duration-500 ease-out ${
              mounted ? "translate-y-0 opacity-70" : "translate-y-10 opacity-0"
            }`}
          />
        </div>

        <div className="absolute bottom-1/2 left-1/2 w-0.25 h-1/2 origin-bottom rotate-[120deg]">
          <div
            className={`w-5 h-5 sm:w-6 sm:h-6 -ml-2.5 sm:-ml-3 mt-4 sm:mt-8 bg-gradient-to-b from-[#A8FFDF]/70 to-[#1A1A32]/70 rounded-full transition-transform duration-500 ease-out ${
              mounted ? "translate-y-0 opacity-70" : "translate-y-10 opacity-0"
            }`}
          />
        </div>

        <div className="absolute bottom-1/2 left-1/2 w-0.25 h-1/2 origin-bottom -rotate-[10deg]">
          <div
            className={`w-3 h-3 sm:w-4 sm:h-4 -ml-1.5 mt-40 sm:mt-64 bg-gradient-to-b from-[#D7A0FF]/70 to-[#1A1A32]/70 rounded-full transition-transform duration-500 ease-out ${
              mounted ? "translate-y-0 opacity-70" : "translate-y-10 opacity-0"
            }`}
          />
        </div>
      </MouseParallax>
    </div>
  );
};