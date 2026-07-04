import express from "express"
import dotenv from "dotenv"
import { sessionMiddleware } from "../Session Manager/sessionConfig.js";
import passport from "../Passport Authentication/passport.index.js";
import { test,login,createTraditionalAccount_Route,checkAccountType} from "../Routes/authentication routes/authenticaticationRoutes.js";
import cors  from "cors";
import { contentRouter } from "../Routes/content routes/content creation/contentRoutes.js";
import mediaRouter from "../Routes/media routes/media.routes.js";
import path from "path"
import multer from "multer"
import { DomainError } from "../Domain Errors/domainErrors.js";
import categoryRouter from "../Routes/category routes/category.routes.js";
import { authenticationRouter } from "../Routes/authentication routes/authenticaticationRoutes.js";
import onboardingRouter from "../Routes/profile routes/onbarding routes/user.onboarding.routes.js";
import { beneficiaryRouter } from "../Routes/profile routes/onbarding routes/beneficiaryRoutes.js";
// configure the dotenv
dotenv.config()


export const app = express();
app.set("trust proxy", 1)
// logic for cors
const allowedOrigins = [
  process.env.LOCALHOST_CLIENT_URL,       // React dev server on your computer   // LAN/Wi-Fi IP for your phone
];
// console.log("My hosts are ",allowedOrigins)


app.use(cors({
  origin: function(origin, callback) {
    if (!origin) return callback(null, true); // Postman or non-browser
    if (allowedOrigins.includes(origin)) {
      return callback(null, true);
    }
    return callback(new Error("CORS not allowed"), false);
  },
  credentials: true,
  cookie:{
          httpOnly: true,
          secure: true,      
          sameSite: "none"
  }
}));


app.use("/uploads", express.static("uploads"));
app.use(express.urlencoded({ extended: true }));
app.use(express.json());
app.use(sessionMiddleware);
app.use(passport.initialize());
app.use(passport.session());
// routes
app.use("/content",contentRouter)
app.use("/media",mediaRouter)
app.use("/category",categoryRouter)
app.use("/auth",authenticationRouter  )
app.use("/onboarding",onboardingRouter)
app.use("/beneficiary", beneficiaryRouter)

// multer storage engine configuration (for article creation)
const storage = multer.diskStorage({
    destination:(req,file,cb)=>{
        const uploadPath = path.join(__dirname, "../Article Creation/Image/uploads")
        cb(null,uploadPath); 
    },
    filename: (req,file,cb)=>{
        // customize the filename (optional)
        const uniqueSuffix = Date.now() + "-" + Math.round(Math.random()  * 1E9)
        cb(null,uniqueSuffix + "-" + file.originalname)
    }
})

const articleUpload = multer({storage});

app.post("/login", (req, res, next) => {
  passport.authenticate("local", (err, user, info) => {
    if (err) return res.status(500).json({ msg: "Error", error: err.message });
    if (!user) return res.status(401).json({ msg: "Invalid credentials" });

    // log in user (establish session)
    req.logIn(user, (err) => {
      if (err) return res.status(500).json({ msg: "Login failed", error: err.message });

      // set cookie manually if you want (optional, usually express-session does it)
      res.status(200).json({ msg: "Login successful", user: { id: user.id, name: user.name } });
    });
    
  })(req, res, next);
});
app.get("/logout",(req,res)=>{

    req.logout((err)=>{
        if(err){
            return res.status(500).json({msg:"Logout failed",error:err.message})
        }
        res.status(200).json({msg:"Logout successful", status:true})
      })
      
})
app.get("/login/account_type",checkAccountType)
app.post("/create_account/traditional",createTraditionalAccount_Route)

// error handling middlewrae
app.use((err, req, res, next) => {
    if(err instanceof DomainError){
        if (err.code === "NOT_FOUND") {
            return res.status(404).json({ message: err.message });
        }
        if (err.code === "INVALID_INPUT") {
            return res.status(400).json({ message: err.message });
        }
    }
    console.error(err);
    return res.status(500).json({ message: "Internal Server Error" });
});
app.listen(process.env.SERVER_PORT || 8000,process.env.HOST,()=>{
    console.log("Server Listening at port ",process.env.SERVER_PORT)
})







