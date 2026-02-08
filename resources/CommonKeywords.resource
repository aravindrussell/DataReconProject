*** Keywords ***

# Common Keywords for Data Comparison Framework

Log Test Header
    [Arguments]    ${test_name}
    Log    ${\n}========================================    console=true
    Log    ${test_name}    console=true
    Log    ========================================    console=true

Log Test Summary
    [Arguments]    ${summary}
    Log    ${\n}--- Comparison Summary ---    console=true
    Log    Matched Records: ${summary}[matched_records]    console=true
    Log    Mismatched Records: ${summary}[mismatched_records]    console=true
    Log    Missing Records: ${summary}[missing_records]    console=true
    Log    Extra Records: ${summary}[extra_records]    console=true
    Log    Overall Status: ${summary}[status]    console=true

Assert Comparison Passed
    [Arguments]    ${comparison_result}
    Should Be Equal    ${comparison_result}[status]    PASSED    msg=Data comparison did not pass

Assert Record Count Match
    [Arguments]    ${source_count}    ${target_count}
    Should Be Equal    ${source_count}    ${target_count}    msg=Record count mismatch

Assert No Missing Records
    [Arguments]    ${missing_count}
    Should Be Equal    ${missing_count}    0    msg=Missing records found in target

Assert Mismatch Below Threshold
    [Arguments]    ${mismatch_percentage}    ${threshold}
    Should Be True    ${mismatch_percentage} <= ${threshold}    msg=Mismatch percentage exceeds threshold

Get Current Timestamp
    Import Library    DateTime
    ${timestamp}=    Get Current Date    result_format=%Y%m%d_%H%M%S
    [Return]    ${timestamp}
