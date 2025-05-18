import { useState } from 'react';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';
import Radio from '@mui/material/Radio';
import RadioGroup from '@mui/material/RadioGroup';
import FormControlLabel from '@mui/material/FormControlLabel';
import FormControl from '@mui/material/FormControl';
import FormLabel from '@mui/material/FormLabel';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';
import Collapse from '@mui/material/Collapse';
import Link from '@mui/material/Link';

import type { ActivityItem, AnswerData } from "../../../types/HealthRecommendations";

export default function ActivityQuestionDialog({
    activityData,
    handleCloseDialog,
    dialogOpen,
}: {
    activityData: ActivityItem,
    handleCloseDialog: (answers?: AnswerData) => void,
    dialogOpen: boolean
}) {
    const [showReason, setShowReason] = useState(false);

    return (
        <Dialog
            open={dialogOpen}
            onClose={() => handleCloseDialog()}
            aria-labelledby="alert-dialog-title"
            aria-describedby="alert-dialog-description"
            keepMounted
        >
            <DialogTitle id="alert-dialog-title">
                <h2>{activityData.activity.recommendation}</h2>
                <Link
                    component="button"
                    variant="body2"
                    onClick={() => setShowReason(!showReason)}
                    sx={{ display: 'block', mt: 1 }}
                >
                    {showReason ? 'Hide why?' : 'See why?'}
                </Link>
                <Collapse in={showReason}>
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                        {activityData.activity.recommendation_reason}
                    </Typography>
                </Collapse>
            </DialogTitle>
            <DialogContent>
                {(activityData.status === 'Not started' || activityData.status === 'Needs user confirmation' || activityData.status === 'Partially completed') &&
                    (
                        <ActivityQuestionList activityData={activityData} handleCloseDialog={handleCloseDialog} />
                    )
                }

                {(activityData.status === 'Completed' || activityData.status === 'Partially completed') && (
                    <div className="supportEvidence">
                        <h3>Supporting Evidence</h3>
                        <p>{activityData.supporting_evidence}</p>
                    </div>
                )}
            </DialogContent>

        </Dialog>
    );
}

function ActivityQuestionList({
    activityData,
    handleCloseDialog,
}: {
    activityData: ActivityItem,
    handleCloseDialog: (answers?: AnswerData) => void
}) {
    {/* Map through user questions providing yes or no options */ }

    const [answers, setAnswers] = useState<AnswerData>({});

    // Handle radio change
    const handleRadioChange = (questionIndex: number, value: 'yes' | 'no') => {
        setAnswers(prev => ({
            ...prev,
            [questionIndex]: value
        }));
    };

    // Submit answers
    const submitAnswers = () => {
        handleCloseDialog(answers);
    };
    return (
        <>
            {
                activityData.user_input_questions?.map((question: string, index: number) => {
                    return (
                        <FormControl key={index} component="fieldset" margin="normal">
                            <FormLabel component="legend">
                                <Typography>{question}</Typography>
                            </FormLabel>
                            <RadioGroup
                                row
                                aria-label={`question-${index}`}
                                name={`question-${index}`}
                                value={answers[index] || ''}
                                onChange={(e) => handleRadioChange(index, e.target.value as 'yes' | 'no')}
                            >
                                <FormControlLabel value="yes" control={<Radio />} label="Yes" />
                                <FormControlLabel value="no" control={<Radio />} label="No" />
                            </RadioGroup>
                        </FormControl>
                    );
                })
            }
            <DialogActions>
                <Button onClick={() => handleCloseDialog()}>Cancel</Button>
                <Button onClick={submitAnswers} autoFocus>Submit</Button>
            </DialogActions>
        </>
    )
}