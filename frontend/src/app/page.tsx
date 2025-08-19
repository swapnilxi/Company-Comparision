import Image from "next/image";
import CompanyCard from "../components/CompanyCard";
import ComparisonChart from "../components/ComparisonChart";
import { CompanyInfo } from "../utils/companyUtils";

// Sample data for demonstration
const sampleCompanies: CompanyInfo[] = [
  {
    id: "company1",
    name: "Tech Innovations Inc.",
    industry: "Technology",
    founded: 2010,
    employees: 1200,
    revenue: 5000000,
    description: "A leading technology company specializing in AI solutions."
  },
  {
    id: "company2",
    name: "Global Finance Group",
    industry: "Finance",
    founded: 1995,
    employees: 3500,
    revenue: 12000000,
    description: "International financial services provider."
  }
];

export default function Home() {
  return (
    <div className="font-sans min-h-screen p-8 pb-20 sm:p-20">
      <main className="max-w-6xl mx-auto">
        <div className="flex items-center justify-between mb-12">
          <Image
            className="dark:invert"
            src="/next.svg"
            alt="Next.js logo"
            width={180}
            height={38}
            priority
          />
          <h1 className="text-2xl font-bold">Company Comparison</h1>
        </div>
        
        <div className="mb-8">
          <h2 className="text-xl font-semibold mb-4">Using JavaScript and TypeScript Together</h2>
          <p className="mb-4">
            This application demonstrates using JavaScript and TypeScript files together in a Next.js project.
            Edit files in <code className="bg-black/[.05] dark:bg-white/[.06] font-mono font-semibold px-1 py-0.5 rounded">src/</code> to see your changes.
          </p>
        </div>
        
        {/* Company Cards Section - TypeScript Component */}
        <div className="mb-12">
          <h2 className="text-xl font-semibold mb-4">Company Cards (TypeScript Component)</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {sampleCompanies.map((company) => (
              <CompanyCard 
                key={company.id} 
                company={company} 
                highlighted={company.id === "company1"} 
              />
            ))}
          </div>
        </div>
        
        {/* Comparison Chart Section - JavaScript Component */}
        <div className="mb-12">
          <h2 className="text-xl font-semibold mb-4">Comparison Chart (JavaScript Component)</h2>
          <ComparisonChart 
            companyIds={sampleCompanies.map(c => c.id)} 
            metric="employees" 
          />
        </div>

        <div className="flex gap-4 items-center flex-col sm:flex-row">
          <a
            className="rounded-full border border-solid border-transparent transition-colors flex items-center justify-center bg-foreground text-background gap-2 hover:bg-[#383838] dark:hover:bg-[#ccc] font-medium text-sm sm:text-base h-10 sm:h-12 px-4 sm:px-5 sm:w-auto"
            href="https://nextjs.org/docs/pages/building-your-application/configuring/typescript"
            target="_blank"
            rel="noopener noreferrer"
          >
            <Image
              className="dark:invert"
              src="/vercel.svg"
              alt="Vercel logomark"
              width={20}
              height={20}
            />
            TypeScript Docs
          </a>
          <a
            className="rounded-full border border-solid border-black/[.08] dark:border-white/[.145] transition-colors flex items-center justify-center hover:bg-[#f2f2f2] dark:hover:bg-[#1a1a1a] hover:border-transparent font-medium text-sm sm:text-base h-10 sm:h-12 px-4 sm:px-5 w-full sm:w-auto md:w-[158px]"
            href="https://nextjs.org/docs/pages/building-your-application/configuring/typescript#mixing-typescript-and-javascript"
            target="_blank"
            rel="noopener noreferrer"
          >
            JS/TS Mixing Guide
          </a>
        </div>
      </main>
      <footer className="row-start-3 flex gap-[24px] flex-wrap items-center justify-center">
        <a
          className="flex items-center gap-2 hover:underline hover:underline-offset-4"
          href="https://nextjs.org/learn?utm_source=create-next-app&utm_medium=appdir-template-tw&utm_campaign=create-next-app"
          target="_blank"
          rel="noopener noreferrer"
        >
          <Image
            aria-hidden
            src="/file.svg"
            alt="File icon"
            width={16}
            height={16}
          />
          Learn
        </a>
        <a
          className="flex items-center gap-2 hover:underline hover:underline-offset-4"
          href="https://vercel.com/templates?framework=next.js&utm_source=create-next-app&utm_medium=appdir-template-tw&utm_campaign=create-next-app"
          target="_blank"
          rel="noopener noreferrer"
        >
          <Image
            aria-hidden
            src="/window.svg"
            alt="Window icon"
            width={16}
            height={16}
          />
          Examples
        </a>
        <a
          className="flex items-center gap-2 hover:underline hover:underline-offset-4"
          href="https://nextjs.org?utm_source=create-next-app&utm_medium=appdir-template-tw&utm_campaign=create-next-app"
          target="_blank"
          rel="noopener noreferrer"
        >
          <Image
            aria-hidden
            src="/globe.svg"
            alt="Globe icon"
            width={16}
            height={16}
          />
          Go to nextjs.org →
        </a>
      </footer>
    </div>
  );
}
