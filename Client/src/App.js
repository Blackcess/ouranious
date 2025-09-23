import { useEffect } from "react";
import "./index.css"
import "./App.css"
import {Routes,Route} from "react-router-dom"
import RecquireAuth from "./Recquire Authentication/RecquireAuth";
import Login from "./Login/Login";
import CreateAccount from "./Account Creation/CreateAccount";
import CreateAccountDone from "./Account Creation/CreateAccountDone";
import Home from "./Home/Home";
import NewsArticle from "./Content Management/Articles/SampleArticle1";
import ThumbnailCard from "./Content Management/Content Thumbnails/ThumbnailCard";
import ParentComponent from "./Parent Page/ParentComponent";
import About from "./About/About"
import ArticleLayout from "./Content Management/Articles/SampleArticle1";
import MyEditor from "./Content Management/In Browser Text Editor/OuraniousTextEditor";
import ArticleUpload from "./Content Management/Upload Page/UploadPage";
import NewsCard from "./Content Management/Articles/NewsCard";
import CategoryPage from "./Content Management/Category Inventory/CategoryTemplate";

function App() {
//  const dummyContent = {
//   title: "The Rise of AI Startups in 2025",
//   author: "Thomas Anesu",
//   published_at: "2025-09-10T12:00:00Z",
//   coverImage: "https://resources.premierleague.pulselive.com/photo-resources/2025/09/13/d3cbe684-d207-49e8-abb6-a9541cdb73b0/Zubimendi.jpg?width=1164",
//   body: `
//     <p>Artificial Intelligence (AI) has moved from being a futuristic idea to the backbone of many modern businesses. In 2025, startups focusing on AI are not just growing—they are defining the next generation of technology and innovation.</p>

//     <h2 id="history">The New Wave of Innovation</h2>
//     <p>Startups in 2025 are leveraging AI to disrupt industries ranging from healthcare to education. Instead of simply automating tasks, these startups are reimagining workflows, reducing costs, and enhancing user experiences.</p>
//     <p>Healthcare startups, for example, are creating AI-driven diagnostic tools that outperform human doctors in certain cases. Meanwhile, in the financial sector, AI-powered fraud detection systems are minimizing risks for banks and consumers alike.</p>

//     <h2>Funding and Growth</h2>
//     <p>Investment in AI startups has skyrocketed. Venture capital firms are allocating larger shares of their funds to AI-based ventures. According to industry reports, global funding for AI startups crossed the $100 billion mark in 2025 alone.</p>
//     <p>This influx of capital allows small teams with groundbreaking ideas to scale rapidly. The barrier to entry for launching an AI company has lowered, thanks to open-source models and cloud-based AI platforms.</p>

//     <h2>Challenges Ahead</h2>
//     <p>Despite the rapid growth, AI startups face challenges. Ethical concerns, data privacy regulations, and competition from tech giants all loom large. Many startups are adopting transparent AI practices, publishing their model architectures, and engaging with regulators early to avoid pitfalls.</p>
//     <p>Another challenge is talent acquisition. The demand for AI engineers and data scientists far exceeds supply, pushing salaries to unprecedented levels. Startups often find themselves competing with tech giants like Google, Amazon, and Microsoft for skilled talent.</p>

//     <h2 id="challenges">The Global Impact</h2>
//     <p>The impact of AI startups is not confined to developed nations. Emerging markets in Africa, Asia, and South America are producing innovative AI companies solving region-specific problems, from agricultural efficiency to language translation for underrepresented dialects.</p>
//     <p>For instance, startups in Africa are using AI to optimize crop yields, while in India, AI-powered education platforms are bridging gaps in rural areas.</p>

//     <h2 id="future">Conclusion</h2>
//     <p>The rise of AI startups in 2025 is more than just a trend—it is a reshaping of the global economy. Those who embrace this transformation will thrive, while others risk being left behind. The journey is just beginning, and the potential is limitless.</p>
//     [media attribute="media1"]
//     <blockquote>
//       "AI is not replacing humans; it is augmenting our capabilities. Startups that understand this balance will lead the way into the future."
//     </blockquote>

//     <p>As we look to 2030, it’s clear that AI startups will not just participate in the economy—they will define it.</p>
//   `,
//   categories: ["Tech", "Startups"],
//   tags: ["AI", "Innovation", "Funding", "Future", "Global"],
// };
  
// "https://elements-resized.envatousercontent.com/envato-dam-assets-production/EVA/TRX/5d/0e/4d/1f/68/v1_E10/E1028W21.jpg?w=800&cf_fit=scale-down&mark-alpha=18&mark=https%3A%2F%2Felements-assets.envato.com%2Fstatic%2Fwatermark4.png&q=85&format=auto&s=aac5c205833748eca936d3110f7989032243975483e7716ce5f5492796818e32";

  return (
    <>
    
      <Routes>
        <Route path="/" element={<RecquireAuth>Landing Page</RecquireAuth>}/>
        <Route path="/login" element={<Login/>}/>
        <Route path="/create_account" element={<CreateAccount/>}/>
        <Route path="/create-account-done" element={<CreateAccountDone/>}/>
        <Route path="/ourans-platform" element={<RecquireAuth><ParentComponent/></RecquireAuth>}>
          <Route path="home" element={<RecquireAuth><Home/></RecquireAuth>}/>
          <Route path="about" element={<RecquireAuth><About/></RecquireAuth>}/>
          {/* <Route path="sample-article" element={<RecquireAuth><ThumbnailCard/></RecquireAuth>}/> */}
          {/* <Route path="contact" element={<RecquireAuth><ArticleLayout /></RecquireAuth>}/> */}
          <Route path="contact" element={<RecquireAuth><ArticleUpload/></RecquireAuth>}/>
          <Route path="category" element={<CategoryPage/>}/>
          <Route path="article/news" element={<ArticleLayout/>}/>
        </Route>
      
      </Routes>
    
    </>
  );
}



export default App;
