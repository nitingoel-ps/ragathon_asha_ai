import styled from 'styled-components';

const StyledScoreDial = styled.div`
    .circularProgressWithLabel {
            width: 100%;
            aspect-ratio: 1;
            .MuiCircularProgress-root{
                width: 100% !important;
                height: auto !important;
            }
            
            .progressForeground{
                color: ${(props) => props.theme.colors.primary};
                .MuiCircularProgress-circle{
                    stroke-linecap:round;
                }
            }
            .progressBackground{
                color: ${(props) => props.theme.colors.surface};
            }
            .progressText{
                color: ${(props) => props.theme.colors.text.secondary};
                font-size: ${(props) => props.theme.typography.fontSize['5xl']};
                font-weight: ${(props) => props.theme.typography.fontWeight.bold};
    
            }

            
        }
`

export default StyledScoreDial