// MUI Components
import CircularProgress from '@mui/material/CircularProgress';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
// Styles
import StyledScoreDial from './ScoreDial.styles';

export default function ScoreDial({ score }: { score: number }) {
    return (
        <StyledScoreDial className="scoreDial">
            <CircularProgressWithLabel value={score} />
        </StyledScoreDial>
    )
}

function CircularProgressWithLabel({ value }: { value: number }) {
    return (
        <Box className="circularProgressWithLabel" sx={{ position: 'relative', display: 'inline-flex' }}>
            <CircularProgress
                className='progressBackground'
                variant="determinate"
                value={100}
                sx={{
                    position: 'absolute',
                    top: 0,
                    left: 0
                }}
            />
            <CircularProgress className='progressForeground' variant="determinate" value={value} />
            <Box
                sx={{
                    top: 0,
                    left: 0,
                    bottom: 0,
                    right: 0,
                    position: 'absolute',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'

                }}
            >
                <Typography className="progressText"
                    component="div"
                >{`${Math.round(value)}`}</Typography>
            </Box>
        </Box >
    );
}

