import styled from "styled-components";
import Accordion from '@mui/material/Accordion';

const StyledCategoryListItem = styled(Accordion)`

    box-shadow: none !important;
    &:before {
        display: none;
    }
    .MuiAccordionSummary-content{
        display: block;
        margin-bottom: 20px;
    }
    .categoryItemHeader{
        display: flex;
        height: fit-content;
        justify-content: space-between;
        margin-bottom: 7px;
        align-items: flex-end;
        h2{
            margin-bottom: 0;
        }
        p {
            margin-bottom: 0;
            color: ${(props) => props.theme.colors.text.tertiary};
        }

    }


    .activityList{
        padding-block: 0px;
        display: flex;
        flex-direction: column;
        gap: 15px;
    }
`

export const StyledActivityListItem = styled.div`
    .activityListItem{display: flex;
    justify-content: space-between;
    align-items: center;
    }
    h3{
        margin-bottom: 0;
    }
    .frequency{
        color: ${(props) => props.theme.colors.text.tertiary};
    }
    .statusIcon{
        scale: 1.6;
        &#completed path{
            
        }
        /* Background of question mark */
        &#needsConfirmation path:first-child{
            opacity: .1;
        }
    }
`

export default StyledCategoryListItem