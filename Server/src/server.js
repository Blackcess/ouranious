import express from "express"
import dotenv from "dotenv"
import { sessionMiddleware } from "../Session Manager/sessionConfig.js";
import passport from "../Passport Authentication/passportConfig.js"
import { test,login,createTraditionalAccount_Route,checkAccountType} from "../Routes/authenticaticationRoutes.js";
import cors  from "cors";
import { contentRouter } from "../Routes/contentRoutes.js";
import { categoryRoute } from "../Routes/categoryRoutes.js";
import { tagRouter } from "../Routes/tagRoutes.js";
import { commentRouter } from "../Routes/commentRoute.js";
import { postAllRouter } from "../Routes/PostAllRoute.js";
import path from "path"
import multer from "multer"
// configure the dotenv
dotenv.config()

export const app = express();
app.use(cors({
    origin:process.env.CLIENT_URL,
    credentials:true
}))
app.use(express.urlencoded({ extended: true }));
app.use(express.json());
app.use(sessionMiddleware);
app.use(passport.initialize());
app.use(passport.session());
// routes
app.use("/content",contentRouter)
app.use("/category",categoryRoute)
app.use("/tag",tagRouter)
app.use("/comments",commentRouter)
app.use("/post/all",postAllRouter)
// app.use("/create-article",express.static("../Article Creation/Image/uploads"))
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

app.post("/createArticle/upload",articleUpload.single("myArticle"),(req,res)=>{
    try {
        console.log("File meta data: ",req.file)
        res.json({msg:"File uploaded Successfully"})
    } catch (error) {
        console.error(error)
        res.status(500).json({err:error})
    }
})
app.get("/test",test)
app.post("/login",passport.authenticate("local"),login)
app.get("/login/account_type",checkAccountType)
app.post("/create_account/traditional",createTraditionalAccount_Route)
app.listen(process.env.SERVER_PORT || 8000,()=>{
    console.log("Server Listening at port ",process.env.SERVER_PORT)
})





