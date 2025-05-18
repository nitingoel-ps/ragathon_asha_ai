import styled from 'styled-components';

export const StyledHealthEngagementPage = styled.div`
    .mainContent{
        padding-inline: 15px;
    }
    .scoreCard{
        display: grid;
        grid-template-columns: 1.2fr 2fr;
        align-items: center;
        gap: 20px;
        margin-block: 20px;
        h1{
            margin-bottom: .6rem;
        }
        p{
            margin-bottom: 0;
        }
        .highlight {
            color: ${(props) => props.theme.colors.primary};
        }
    }
    .fullWidthImage {
        width: 100vw;
    }
`