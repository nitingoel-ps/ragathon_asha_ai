import styled from 'styled-components';

export const StyledHealthEngagementPage = styled.div`
    .mainContent{
        padding-inline: 15px;
    }
    .scoreCard{
        display: grid;
        grid-template-columns: 1.2fr 2fr;
        gap: 20px;
        margin-block: 20px;
        .highlight {
            color: ${(props) => props.theme.colors.primary};
        }
        .circularProgressWithLabel {
            width: 100%;
            aspect-ratio: 1;
            .MuiCircularProgress-root{
                width: 100% !important;
                height: auto !important;
            }
            
            .progressForeground{
                color: ${(props) => props.theme.colors.primary};
            }
            .progressBackground{
                color: ${(props) => props.theme.colors.surface};
            }
            .progressText{
                color: ${(props) => props.theme.colors.text.secondary};
                font-size: ${(props) => props.theme.typography.fontSize['4xl']};
                font-weight: ${(props) => props.theme.typography.fontWeight.bold};
    
            }

            
        }
    }
    .fullWidthImage {
        width: 100vw;
    }
`