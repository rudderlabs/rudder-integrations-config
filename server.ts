import express from 'express';

const app = express();
const PORT = process.env.SERVER_PORT || 8432;

app.use(express.json());

app.get('/', (req,res)=> {
    res.send(`Server is listening on port ${PORT}`);
})
app.listen(PORT);