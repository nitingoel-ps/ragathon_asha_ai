import LinearProgress, { linearProgressClasses } from '@mui/material/LinearProgress';
import styled from 'styled-components';

const ProgressBar = styled(LinearProgress)(({ theme, barColor }) => ({
    borderRadius: 5,
    [`&.${linearProgressClasses.colorPrimary}`]: {
        backgroundColor: theme.colors.surface,
        height: '7px'
    },
    [`& .${linearProgressClasses.bar}`]: {
        borderRadius: 5,
        backgroundColor: barColor
    },
}));

export default ProgressBar