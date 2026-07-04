import "./index.css"
import "./App.css"
import {Routes,Route} from "react-router-dom"
import RecquireAuth from "./Recquire Authentication/RecquireAuth";
import {Login} from "./Login/Login";
import { CreateAccount } from "./Account Creation/CreateAccount";
import CreateAccountDone from "./Account Creation/CreateAccountDone";
import Home from "./Home/Home";
import ParentComponent from "./Parent Page/ParentComponent";
import About from "./About/About"
import ArticleLayout from "./Content Management/Articles/MyArticles";
import AdminLayout from "./Admnistration Section/Admin Layout/AdminSection";
import ArticleEditorPage from "./Admnistration Section/Quill Section/Quill Editor/ArticleCreationCenter";
import ArticleViewPage from "./Content Management/Articles/Content Documents Style/ArticleViewPage";
import { CategoryPageWrapper } from "./Content Management/Articles/Content Documents Style/Categories/Category page/CategoryPage";
import LandingPage from "./Landing Page/LandingPage";
import OnboardingStepper from "./Account Creation/onboarding/steps/main stepper/MainStepperWrapper";
import { JoinCommunity } from "./Community/Join Community/JoinCommunity";
import { PublishedArticles } from "./Admnistration Section/Admin Layout/My Articles/published articles/PublishedArticles";
import {DraftArticles} from "./Admnistration Section/Admin Layout/My Articles/draft articles/DraftArticles"

function App() {
  
  return (
    <>

      <Routes>
        <Route path="/login" element={<Login/>}/>
        <Route path="/create_account" element={<CreateAccount/>}/>
        <Route path="/create-account-done" element={<CreateAccountDone/>}/>
        <Route path="/landing" element={<LandingPage/>}/>
        <Route path="/onboarding" element={<OnboardingStepper/>}/>
        <Route path="/" element={<RecquireAuth><ParentComponent/></RecquireAuth>}>
          <Route index element={<Home/>}/>
          <Route path="home" element={<Home/>}/>
          <Route path="about" element={<About/>}/>
          <Route path="article/news" element={<ArticleLayout/>}/>
          <Route path="view/:slug" element={<ArticleViewPage />}/>
          <Route path="category/:id" element={<CategoryPageWrapper />}/>
          <Route path="uploads" element={<ArticleEditorPage />}/>
          <Route path="community" element ={<JoinCommunity/>} />
          <Route path="admin" element={<AdminLayout/>}>
            <Route index element= {<PublishedArticles/>}/>
            <Route path="published" element= {<PublishedArticles/>}/>
            <Route path="drafts" element= {<DraftArticles/>}/>
          </Route>
        </Route>
      
      </Routes>
    
    </>
  );
}




export default App;







































